import typing
import datetime

import pytest
import dotenv

import huggingface_hub

from twon_lss.utility import Noise, Decay, LLM, Message, Chat


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

        print(llm.generate(Chat([Message(role="user", content=SAMPLES[0])])))

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

    def test_single_call(self, noise: Noise):
        value = noise()
        assert isinstance(value, float)
        assert noise.low <= value <= noise.high

    def test_bounds(self, noise: Noise, noise_samples: typing.List[float]):
        assert noise.low <= min(noise_samples)
        assert max(noise_samples) <= noise.high

    def test_distribution(self, noise: Noise, noise_samples: typing.List[float]):
        expected_mean = (noise.low + noise.high) / 2
        actual_mean = sum(noise_samples) / len(noise_samples)
        assert actual_mean == pytest.approx(expected_mean, abs=1e-3)

    def test_draw_samples_length(self, noise: Noise):
        samples = noise.draw_samples(100)
        assert len(samples) == 100
        assert all(isinstance(s, float) for s in samples)


class TestDecay:
    @pytest.fixture
    def decay(self) -> Decay:
        return Decay()

    def test_create(self, decay: Decay):
        assert decay.minimum == 0.2
        assert decay.timedelta == datetime.timedelta(days=3)

    def test_same_time(self, decay: Decay, ref_datetime: datetime.datetime):
        factor = decay(ref_datetime, ref_datetime)
        assert factor == pytest.approx(1.0, abs=1e-3)

    def test_past_reference_time(
        self,
        decay: Decay,
        ref_datetime: datetime.datetime,
        ref_timedelta: datetime.timedelta,
    ):
        factor = decay(ref_datetime - ref_timedelta, ref_datetime)
        assert factor == pytest.approx(decay.minimum, abs=1e-3)

    def test_intermediate_time(self, decay: Decay, ref_datetime: datetime.datetime):
        half_time = ref_datetime - decay.timedelta / 2
        factor = decay(half_time, ref_datetime)
        assert decay.minimum < factor < 1.0

    def test_decay_monotonic(self, decay: Decay, ref_datetime: datetime.datetime):
        times = [
            ref_datetime,
            ref_datetime - datetime.timedelta(days=1),
            ref_datetime - datetime.timedelta(days=2),
            ref_datetime - datetime.timedelta(days=3),
        ]

        factors = [decay(time, ref_datetime) for time in times]

        for i in range(len(factors) - 1):
            assert factors[i] >= factors[i + 1]
