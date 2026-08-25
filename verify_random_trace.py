#!/usr/bin/env python3
"""Compare an extracted one-trace SEG-Y with a trace in the original file."""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path


SAMPLE_BYTES = {
    1: 4,   # IBM float
    2: 4,   # int32
    3: 2,   # int16
    4: 4,   # fixed point with gain
    5: 4,   # IEEE float32
    6: 8,   # IEEE float64
    7: 3,   # int24
    8: 1,   # int8
    9: 8,   # int64
    10: 4,  # uint32
    11: 2,  # uint16
    12: 8,  # uint64
    15: 3,  # uint24
    16: 1,  # uint8
}


def be_u16(data: bytes) -> int:
    return int.from_bytes(data, "big", signed=False)


def read_exact(stream, size: int, description: str) -> bytes:
    data = stream.read(size)
    if len(data) != size:
        raise ValueError(f"truncated SEG-Y while reading {description}")
    return data


def original_trace(path: Path, trace_index: int) -> tuple[bytes, bytes, int, int]:
    file_size = path.stat().st_size
    with path.open("rb") as stream:
        mandatory = read_exact(stream, 3600, "textual and binary headers")
        binary = mandatory[3200:3600]
        default_samples = be_u16(binary[20:22])
        sample_format = be_u16(binary[24:26])
        extended_headers = int.from_bytes(binary[304:306], "big", signed=True)
        if extended_headers < 0:
            raise ValueError("unknown extended textual header count is unsupported")
        if sample_format not in SAMPLE_BYTES:
            raise ValueError(f"unsupported SEG-Y sample format code: {sample_format}")

        extended = read_exact(
            stream,
            extended_headers * 3200,
            "extended textual headers",
        )
        global_headers = mandatory + extended

        for current_trace in range(trace_index + 1):
            header = stream.read(240)
            if not header:
                raise IndexError(
                    f"trace index {trace_index} is outside the original SEG-Y file"
                )
            if len(header) != 240:
                raise ValueError("truncated SEG-Y trace header")

            sample_count = be_u16(header[114:116]) or default_samples
            if sample_count == 0:
                raise ValueError(f"trace {current_trace} has no sample count")
            payload_size = sample_count * SAMPLE_BYTES[sample_format]

            if current_trace == trace_index:
                payload = read_exact(stream, payload_size, "selected trace samples")
                return global_headers, header + payload, sample_format, sample_count

            stream.seek(payload_size, 1)
            if stream.tell() > file_size:
                raise ValueError("truncated SEG-Y trace samples")

    raise IndexError(f"trace index {trace_index} was not found")


def decode_samples(payload: bytes, sample_format: int, count: int = 10) -> list[int | float]:
    width = SAMPLE_BYTES[sample_format]
    values: list[int | float] = []
    for index in range(min(count, len(payload) // width)):
        sample = payload[index * width : (index + 1) * width]
        if sample_format == 1:
            bits = int.from_bytes(sample, "big")
            if bits == 0:
                value = 0.0
            else:
                sign = -1.0 if bits & 0x80000000 else 1.0
                exponent = ((bits >> 24) & 0x7F) - 64
                fraction = (bits & 0x00FFFFFF) / float(1 << 24)
                value = sign * fraction * (16.0**exponent)
        elif sample_format in (2, 4):
            value = struct.unpack(">i", sample)[0]
        elif sample_format == 3:
            value = struct.unpack(">h", sample)[0]
        elif sample_format == 5:
            value = struct.unpack(">f", sample)[0]
        elif sample_format == 6:
            value = struct.unpack(">d", sample)[0]
        elif sample_format == 7:
            value = int.from_bytes(sample, "big", signed=True)
        elif sample_format == 8:
            value = struct.unpack(">b", sample)[0]
        elif sample_format == 9:
            value = struct.unpack(">q", sample)[0]
        elif sample_format == 10:
            value = struct.unpack(">I", sample)[0]
        elif sample_format == 11:
            value = struct.unpack(">H", sample)[0]
        elif sample_format == 12:
            value = struct.unpack(">Q", sample)[0]
        elif sample_format == 15:
            value = int.from_bytes(sample, "big", signed=False)
        else:  # format 16
            value = sample[0]
        values.append(value)
    return values


def print_samples(original: list[int | float], extracted: list[int | float]) -> None:
    print("First 10 samples:")
    print(f"  {'Index':>5}  {'Original':>20}  {'Byte2Bit decompressed':>22}")
    for index in range(max(len(original), len(extracted))):
        left = str(original[index]) if index < len(original) else "<missing>"
        right = str(extracted[index]) if index < len(extracted) else "<missing>"
        print(f"  {index:5d}  {left:>20}  {right:>22}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compare an already extracted one-trace SEG-Y byte-for-byte with "
            "the same trace in the original SEG-Y file."
        )
    )
    parser.add_argument("original", type=Path, help="original SEG-Y file")
    parser.add_argument("extracted", type=Path, help="one-trace SEG-Y produced by extractTrace")
    parser.add_argument("trace", type=int, help="zero-based trace index")
    args = parser.parse_args()

    if args.trace < 0:
        parser.error("trace must be zero or greater")

    original = args.original.resolve()
    extracted = args.extracted.resolve()
    if not original.is_file():
        parser.error(f"original SEG-Y file not found: {original}")
    if not extracted.is_file():
        parser.error(f"extracted SEG-Y file not found: {extracted}")

    try:
        global_headers, trace_record, sample_format, sample_count = original_trace(
            original, args.trace
        )
        expected = global_headers + trace_record
        actual = extracted.read_bytes()
        print_samples(
            decode_samples(trace_record[240:], sample_format),
            decode_samples(actual[len(global_headers) + 240 :], sample_format),
        )

        if actual != expected:
            global_match = actual[: len(global_headers)] == global_headers
            trace_match = actual[len(global_headers) :] == trace_record
            print(f"FAIL: trace {args.trace} does not match", file=sys.stderr)
            print(f"  global headers match: {global_match}", file=sys.stderr)
            print(f"  trace record matches:  {trace_match}", file=sys.stderr)
            return 6

        print(f"PASS: trace {args.trace} matches byte-for-byte")
        print(f"  sample format code: {sample_format}")
        print(f"  samples:            {sample_count}")
        print(f"  compared bytes:     {len(expected)}")
        return 0
    except (OSError, ValueError, IndexError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
