import statistics
import pandas as pd
import pydantic
import json
import typing
import plotly.graph_objects as go
import plotly.express as px
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
from twon_lss.utility.llm import LLM
import numpy as np
from sklearn.decomposition import PCA
import umap


class VisualizeRun(pydantic.BaseModel):

    path: str
    embedding_model: LLM = None

    df: pd.DataFrame = None
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    def model_post_init(self, __context: typing.Any):

        data = json.loads(open(self.path).read())

        results_parsed = []
        for elem in data:
            results_parsed.append({
                "user": elem["user"]["id"],
                "tweet": elem["content"],
                "created_at": elem["timestamp"],
                "like_count": len(elem["likes"]),
                "read_count": len(elem["reads"]),
                "embedding": elem["embedding"] if "embedding" in elem else None
            })

        self.df = pd.DataFrame(results_parsed)

        if (self._has_embeddings() == False) and self.embedding_model:
            self._ensure_embeddings()
        else:
            self._load_embeddings()


    # Embedding Handling
    def _ensure_embeddings(self):
        if not self._load_embeddings():
            self._generate_embeddings()
            
    def _load_embeddings(self) -> bool:
        try:
            self.df["embedding"] = list(np.load(f"{self.path}_embeddings.npz")["embeddings"])
            print("Found existing embeddings.")
            return True
        except FileNotFoundError:
            pass
        return False

    def _has_embeddings(self) -> bool:
        return not self.df["embedding"].isnull().any()

    def _generate_embeddings(self):
        print("Generating embeddings...")
        embeddings: list = []
        for i in range(0, len(self.df), 500):
            embeddings.extend(self.embedding_model.extract(self.df["tweet"].tolist()[i:i+500])) # There is apparently a limit on the number of texts that can be processed at once
        self.df["embedding"] = embeddings

        # Save embeddings
        np.savez(f"{self.path}_embeddings.npz",
                embeddings=np.array(self.df["embedding"].to_list())
        )
        print(f"Saved embeddings to {self.path}_embeddings.npz")



    # View and Like related metrics
    def plot_cumulative_views(self) -> go.Figure:
        
        fig = go.Figure()

        for username in self.df["user"].unique():
            df_user = self.df[self.df["user"] == username].copy()
            df_user = df_user.sort_values("created_at")
            df_user["cumulative_views"] = df_user["read_count"].cumsum()
    
            fig.add_trace(go.Scatter(
                x=df_user["created_at"], 
                y=df_user["cumulative_views"], 
                mode='lines+markers', 
                name=username
            ))
    
        fig.update_layout(
            title="Cumulative View Count per User Over Time",
            xaxis_title="Time Step",
            yaxis_title="Cumulative Views"
        )
        return fig
    

    def plot_view_distribution(self) -> go.Figure:

        fig = go.Figure()

        for username in self.df["user"].unique():
            df_user = self.df[self.df["user"] == username].copy()
            df_user = df_user.sort_values("created_at")

            fig.add_trace(go.Scatter(
                x=df_user["created_at"], 
                y=df_user["read_count"], 
                mode='lines+markers', 
                name=username
            ))

        fig.update_layout(
            title="View Count per User Over Time",
            xaxis_title="Time Step",
            yaxis_title="View Count"
        )

        return fig


    def plot_cumulative_likes(self) -> go.Figure:
        fig = go.Figure()

        for username in self.df["user"].unique():
            df_user = self.df[self.df["user"] == username].copy()
            df_user = df_user.sort_values("created_at")
            df_user["cumulative_likes"] = df_user["like_count"].cumsum()
    
            fig.add_trace(go.Scatter(
                x=df_user["created_at"], 
                y=df_user["cumulative_likes"], 
                mode='lines+markers', 
                name=username
            ))
    
        fig.update_layout(
            title="Cumulative Like Count per User Over Time",
            xaxis_title="Time Step",
            yaxis_title="Cumulative Likes"
        )
        return fig

    def plot_like_distribution(self) -> go.Figure:

        fig = go.Figure()

        for username in self.df["user"].unique():
            df_user = self.df[self.df["user"] == username].copy()
            df_user = df_user.sort_values("created_at")

            fig.add_trace(go.Scatter(
                x=df_user["created_at"], 
                y=df_user["like_count"], 
                mode='lines+markers', 
                name=username
            ))

        fig.update_layout(
            title="Like Count per User Over Time",
            xaxis_title="Time Step",
            yaxis_title="Like Count"
        )

        return fig

    def plot_likes_given_by_round(self) -> go.Figure:

        fig = go.Figure()

        df_likes_grouped = self.df.groupby("created_at")["like_count"].sum().reset_index()

        fig.add_trace(go.Scatter(
            x=df_likes_grouped["created_at"],
            y=df_likes_grouped["like_count"],
            mode='lines+markers',
            name="Total Likes Given"
        ))

        return fig

    # Embedding related metrics
    def plot_pairwise_similarity_over_time(self) -> go.Figure:

        results_dict = self._calculate_pairwise_similarity_over_time()

        plot_data = []
        for user_pair, similarities in results_dict.items():
            user1, user2 = user_pair
            pair_name = f"{user1} - {user2}"

            # Get timestamps for this pair (assuming similarities are ordered by timestamp)
            timestamps = list(range(1, len(similarities) + 1))  # Start from 1 since we skip timestamp 0

            for timestamp, similarity in zip(timestamps, similarities):
                plot_data.append({
                    'user_pair': pair_name,
                    'timestamp': timestamp,
                    'similarity': similarity
                })
        
        # Create DataFrame for plotting
        plot_df = pd.DataFrame(plot_data)
        
        # Create interactive plot with plotly
        fig = px.line(plot_df, 
                      x='timestamp', 
                      y='similarity', 
                      color='user_pair',
                      title='Tweet Similarity Over Time by User Pairs',
                      labels={'timestamp': 'Timestamp', 'similarity': 'Similarity Score'},
                      hover_data=['user_pair'])
        
        fig.update_layout(
            width=1200,
            height=600,
            showlegend=False  # Hide legend due to many lines
        )

        return fig


    def _calculate_pairwise_similarity_over_time(self) -> go.Figure:

        results_dict = defaultdict(list)

        for timestamp in self.df["created_at"].unique():
            temp_df = self.df[self.df["created_at"] == timestamp].copy()

            if timestamp == 0:
                continue  # Skip the first timestamp if it is zero
    
            for base_user in temp_df["user"]:
            
                similarity = cosine_similarity(
                    [temp_df[temp_df["user"] == base_user]["embedding"].values[0]],
                    temp_df[temp_df["user"] != base_user]["embedding"].tolist()
                )
    
                for other_user, similarity in zip(temp_df[temp_df["user"] != base_user]["user"], similarity[0]):
                
                    # determine which user is earlier in the alphabet for position
                    if other_user < base_user:
                        position = (other_user, base_user)
                    else:
                        position = (base_user, other_user)
    
                    if len(results_dict[position]) < timestamp:
                        results_dict[position].append(similarity)

        return results_dict


    def plot_semantic_distribution(self) -> go.Figure:
        if self._has_embeddings() == False:
            raise ValueError("Embeddings are not available for visualization.")

        reducer = umap.UMAP(
            n_components=2,           # 2D for visualization, 5-50 for downstream ML
            n_neighbors=15,           # 15-30 for semantic data
            min_dist=0.0,            # 0.0 for tight clusters, 0.1-0.5 for separation
            metric='cosine',          # Critical for semantic embeddings
            random_state=42,          # Reproducibility
            n_epochs=200,            # More epochs for better convergence
            negative_sample_rate=5    # Balance speed vs quality
        )
        # Reduce dimensions using UMAP for visualization
        embeddings_2d = reducer.fit_transform(np.array(self.df["embedding"].to_list()))

        plot_df = self.df.copy()
        plot_df['dim1'] = embeddings_2d[:, 0]
        plot_df['dim2'] = embeddings_2d[:, 1]
        plot_df["like_count"] = plot_df["like_count"].apply(lambda x: x if x > 0 else 1)

        fig = px.scatter(plot_df, 
                         x='dim1', 
                         y='dim2', 
                         color='user',
                         animation_group='user',
                         animation_frame='created_at',
                         title='Semantic Distribution of Tweets',
                         size='like_count'
                         )

        fig.update_layout(
            width=800,
            height=600
        )
        
        return fig

    def plot_embedding_distance_to_oneself(self) -> go.Figure:
        """
        At each step calculate the distance of the current 5 embeddings to the first 5 embeddings for each user
        """

        fig = go.Figure()

        for user in self.df["user"].unique():
            user_df = self.df[self.df["user"] == user]
            
            # Calculate distances to the first 5 embeddings
            distances = [
                statistics.mean([
                    statistics.mean(cosine_similarity(user_df["embedding"][i-5:i].to_list(), user_df["embedding"][:5].to_list())[j]) 
                    for j in range(5)
                ])
                for i in range(5, len(user_df)-5)
            ]

            fig.add_trace(go.Scatter(
                x=list(range(5, user_df.shape[0])),
                y=distances,
                mode='lines+markers',
                name=user
            ))

        fig.update_layout(
            title="Embedding Distance to Oneself Over Time",
            xaxis_title="Time Step",
            yaxis_title="Cosine Similarity",
            width=800,
            height=600
        )

        return fig
