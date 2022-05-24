import lib

if __name__ == "__main__":
    reader = lib.Reader("Dane_S2_100_20.xlsx")
    process = lib.Processor(reader.data)
    writer = lib.Writer(process.solutionDataFrame)
