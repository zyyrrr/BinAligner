# BinAligner

This is the repository of the paper *BINALIGNER: Aligning Binary Code for Cross-Compilation Environment Diffing* (Accepted by NDSS 2026)

## Environment

- python                    3.7
- pytorch                   1.12

## Dataset

The sample dataset comes from the cross-architecture scenario.

## Usage

Run the following code to obtain candidate subgraph pairs:
```bash
python obtain_candidate_subgraph_pairs.py
```

We modify the open source code provided by [Gemini](https://github.com/xiaojunxu/dnn-binary-code-similarity) to implement the third step of BinAligner (i.e., Aligned Subgraph Pair Decision).
```bash
python Gemini_for_Aligned_Subgraph_Pair_Decision/detection.py
```