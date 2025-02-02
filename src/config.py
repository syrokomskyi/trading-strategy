from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ExtractorConfig:
    webp_quality: int = 84
    max_workers: int = 4
    scale_width: int | None = None
    scale_height: int | None = None
    lossless: bool = False
    compression_method: int = 6
    output_format: str = "webp"
