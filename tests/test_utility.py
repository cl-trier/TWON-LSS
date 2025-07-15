import typing
import datetime

import pytest
import dotenv

import huggingface_hub

from twon_lss.utility import Noise, Decay, LLM


CFG = dotenv.dotenv_values(".env")

SAMPLES: typing.List[str] = [
    "I like cookies.",
    "I love cookies.",
    "I hate sweets.",
    "Sushi is the best food.",
    "Try to touch the past. Try to deal with the past.",
]


class TestLLM:
    @pytest.fixture
    def client(self) -> huggingface_hub.InferenceClient:
        return huggingface_hub.InferenceClient(api_key=CFG["HF_TOKEN"])

    def test_generate(self, client: huggingface_hub.InferenceClient):
        # The Llama 3 Herd of Models
        # https://doi.org/10.48550/arXiv.2407.21783
        model: str = "meta-llama/Meta-Llama-3-8B-Instruct"
        llm = LLM(client=client, model=model)

        print(llm.generate([{"role": "user", "content": SAMPLES[0]}]))

    def test_embed(self, client: huggingface_hub.InferenceClient):
        # BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation
        # https://doi.org/10.48550/arXiv.2402.03216
        model: str = "BAAI/bge-m3"
        llm = LLM(client=client, model=model)

        print(llm.embed(SAMPLES[0]))

    def test_similarity(self, client: huggingface_hub.InferenceClient):
        # BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation
        # https://doi.org/10.48550/arXiv.2402.03216
        model: str = "BAAI/bge-m3"
        llm = LLM(client=client, model=model)

        print(llm.similarity(SAMPLES[0], SAMPLES))

    def test_classification(self, client: huggingface_hub.InferenceClient):
        # SuperTweetEval: A Challenging, Unified and Heterogeneous Benchmark for Social Media NLP Research
        # Findings of the Association for Computational Linguistics: EMNLP 2023
        # https://doi.org/10.18653/v1/2023.findings-emnlp.838
        model: str = "cardiffnlp/twitter-roberta-base-topic-sentiment-latest"
        # ALT(offensiveness) model: str = "cardiffnlp/twitter-roberta-base-offensive"
        # ALT(topics): model: str = "cardiffnlp/tweet-topic-21-multi"
        llm = LLM(client=client, model=model)

        for sample in SAMPLES:
            print(llm.classification(sample))


class TestNoise:
    @pytest.fixture
    def noise(self) -> Noise:
        return Noise()

    @pytest.fixture
    def noise_samples(self, noise: Noise, num_observations: int) -> typing.List[float]:
        return noise.draw_samples(num_observations)

    def test_noise_bounds(self, noise: Noise, noise_samples: typing.List[float]):
        assert noise.low <= min(noise_samples)
        assert max(noise_samples) <= noise.high

    def test_noise_distribution(self, noise: Noise, noise_samples: typing.List[float]):
        assert sum(noise_samples) / len(noise_samples) == pytest.approx(
            sum([noise.low, noise.high]) / 2, abs=1e-3
        )


class TestUtility:
    @pytest.fixture
    def decay(self) -> Decay:
        return Decay()

    def test_decay_abs_now(self, decay: Decay, ref_datetime: datetime.datetime):
        assert decay(ref_datetime, ref_datetime) == pytest.approx(1.0, abs=1e-3)

    def test_decay_abs_past(
        self,
        decay: Decay,
        ref_datetime: datetime.datetime,
        ref_timedelta: datetime.timedelta,
    ):
        assert decay(ref_datetime - ref_timedelta, ref_datetime) == pytest.approx(
            decay.minimum, abs=1e-3
        )
