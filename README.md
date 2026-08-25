# Byte2Bit SEG-Y Compression Tool

Byte2Bit SEG-Y is a lossless compression tool for seismic SEG-Y data.

It is designed for teams that work with large seismic datasets and want to reduce storage requirements without changing the underlying data. The original SEG-Y file is recovered exactly after decompression.

## Why try it?

Seismic datasets can become very large, making storage, transfer and access increasingly expensive.

Byte2Bit is designed to reduce that footprint while keeping the data lossless and allowing efficient access to compressed data.

Byte2Bit provided:

* Up to **71.4% storage reduction**
* Up to **3.50:1 compression ratio**
* About **1.55× more total storage savings than ZIP in optimum compression mode**
* Around **600× faster chunk access than ZIP** in our tested access workflow

## Benchmark results

The datasets below are anonymized because the original filenames and data sources are covered by confidentiality agreements.

| Dataset                  |       Original size |       Byte2Bit size |     Storage saved |  Reduction | Compression ratio |
| ------------------------ | ------------------: | ------------------: | ----------------: | ---------: | ----------------: |
| Seismic Dataset A        |    33,839,532 bytes |    26,662,170 bytes |   7,177,362 bytes |     21.21% |            1.27:1 |
| Seismic Dataset B        | 3,392,189,388 bytes | 2,672,211,455 bytes | 719,977,933 bytes |     21.22% |            1.27:1 |
| Seismic Velocity Dataset |   186,272,760 bytes |    53,262,647 bytes | 133,010,113 bytes | **71.41%** |        **3.50:1** |

Compression depends on the structure and characteristics of the seismic data, so results will vary between datasets.

## Byte2Bit vs ZIP

We also compared Byte2Bit with ZIP using its optimum compression setting.

Across the tested SEG-Y datasets, Byte2Bit produced approximately:

**1.55× more total storage savings than ZIP.**

Byte2Bit is also designed around compressed-data access rather than treating the complete dataset as one archive.

In our chunk-access benchmark, accessing the required data from the Byte2Bit-compressed representation was approximately:

**600× faster than accessing the equivalent data through ZIP.**

This can be especially useful when an application needs only part of a large seismic dataset rather than the entire file.

## Try it on your own SEG-Y data

The best way to evaluate a compression tool is with your own data.

Download the evaluation version, select one of your SEG-Y files and compare:

* Original file size
* Compressed file size
* Storage reduction
* Compression ratio
* Compression time
* Decompression time
* Data integrity after decompression

No modification of the original SEG-Y data is required.

## Lossless compression

Byte2Bit compression is **lossless**.

After decompression, the reconstructed SEG-Y data is identical to the original input. This makes the tool suitable for workflows where seismic values must not be altered.

## Download

Download the latest evaluation version from the **Releases** section of this repository.

The release package contains:

* Byte2Bit SEG-Y executable
* User manual
* Instructions for compression and decompression

## We would like to see your results

SEG-Y datasets can differ significantly depending on acquisition, processing stage and the type of information stored in the traces.

If you try Byte2Bit on your own dataset, we would be very interested to hear:

* Your compression ratio
* Storage reduction
* Dataset type
* Compression and decompression performance

If the results are interesting, we can also benchmark Byte2Bit on a representative dataset from your workflow.

## Contact

**Byte2Bit ApS**

Data compression for large scientific and numerical datasets.

https://byte2bit.io
