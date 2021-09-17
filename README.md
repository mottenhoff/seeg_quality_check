# Seeg quality check
Check data for irregularities

`pip install -r requirements.txt`

Tested with python 3.9.2

### Usage
1) Copy files to a folder

In a new file:
2) `import check_quality`
3) `qc = check_quality.QualityChecker()`
4) `qc.run_all( eeg: np.array,
                timestamps: np.array,
                fs: Union[int, float],
                channel_names: list=None,
                return_all_flagged_channels: bool=False,
                plot: bool=False)`

---

Numerical retrieval of non-eeg channel is unstable and currently not recommended
