import asyncio
from dataclasses import dataclass
import ffmpeg
from PIL import Image
from pathlib import Path
from typing import Sequence

from .config import ExtractorConfig
from .utils import (
    setup_logger,
    validate_timeframes,
    ensure_output_path,
    clean_failed_output,
)


@dataclass(slots=True)
class VideoInfo:
    duration: int
    width: int
    height: int


class FrameExtractor:
    def __init__(
        self,
        input_video: str | Path,
        output_folder: str | Path,
        config: ExtractorConfig = ExtractorConfig(),
    ):
        self.input_video = Path(input_video)
        # Create subfolder with video filename (without extension)
        self.output_folder = ensure_output_path(
            Path(output_folder) / self.input_video.stem
        )
        self.config = config
        self.logger = setup_logger("FrameExtractor")

    def _get_video_info(self) -> VideoInfo:
        probe = ffmpeg.probe(self.input_video)
        video_stream = next(s for s in probe["streams"] if s["codec_type"] == "video")

        duration = int(float(probe.get("format", {}).get("duration", 0)))
        match duration:
            case 0:
                self.logger.warning(
                    "Could not determine video duration from format info"
                )
                duration = int(float(video_stream.get("duration", 0)))
                if duration == 0:
                    raise ValueError("Could not determine video duration")

        return VideoInfo(
            duration=duration,
            width=int(video_stream["width"]),
            height=int(video_stream["height"]),
        )

    async def extract_frame(self, timeframe: int, index: int) -> None:
        # Convert seconds to HH:MM:SS format
        hours = timeframe // 3600
        minutes = (timeframe % 3600) // 60
        seconds = timeframe % 60
        timestamp = f"{hours:02d}{minutes:02d}{seconds:02d}"

        output_filename = (
            self.output_folder / f"{timestamp}.{self.config.output_format}"
        )

        try:
            stream = ffmpeg.input(self.input_video, ss=timeframe)

            if self.config.scale_width or self.config.scale_height:
                stream = stream.filter(
                    "scale",
                    self.config.scale_width or -1,
                    self.config.scale_height or -1,
                )

            process = stream.output(str(output_filename), vframes=1).overwrite_output()
            await asyncio.to_thread(
                process.run, capture_stdout=True, capture_stderr=True
            )

            async with asyncio.TaskGroup() as tg:
                tg.create_task(
                    asyncio.to_thread(
                        self._optimize_image,
                        output_filename,
                    )
                )

            self.logger.info(f"Frame extracted at {timeframe}s → {output_filename}")

        except* (ffmpeg.Error, IOError) as eg:
            self.logger.error(f"Error extracting frame at {timeframe}s: {eg!r}")
            clean_failed_output(output_filename)

    def _optimize_image(self, filename: Path) -> None:
        with Image.open(filename) as img:
            img.save(
                filename,
                self.config.output_format.upper(),
                quality=self.config.webp_quality,
                method=self.config.compression_method,
                lossless=self.config.lossless,
            )

    async def process_timeframes(self, timeframes: Sequence[int]) -> None:
        try:
            video_info = self._get_video_info()
            valid_timeframes = validate_timeframes(timeframes, video_info.duration)

            if len(valid_timeframes) != len(timeframes):
                self.logger.warning(
                    f"Skipped {len(timeframes) - len(valid_timeframes)} invalid timeframes"
                )

            async with asyncio.TaskGroup() as tg:
                for index, timeframe in valid_timeframes:
                    tg.create_task(self.extract_frame(timeframe, index))

        except* Exception as eg:
            self.logger.error(f"Error processing video: {eg!r}")
            raise
