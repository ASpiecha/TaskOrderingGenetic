"""
Task Ordering problem solution
- using genetic algorithm
- order crossover
- marked crossover (TBD)
- random swap mutation
Module includes 3 classes:
1. Reader
2. Processor
3. Writer
Originally created to compare computations results with changing input parameters (pm, pc, generations, population size)
Reduced to single-run for readibility on Git public repository
"""

import pandas as pd
import copy
import random


class Reader:
    """ A class used to import data with tasks duration"""
    def __init__(self, filename):
        self.df = self.importData(filename, "Arkusz1")
        self.data = self.convertDFtoList(self.df)

    def importData(self, path, sheetname):
        file = pd.read_excel(path, sheet_name=sheetname, engine="openpyxl")
        df = pd.DataFrame(file)
        return df

    def convertDFtoList(self, df):
        newList = df.values.tolist()
        return newList


class Processor:
    def __init__(self, data, populationSize=50, pc=0.9, pm=0.02, generations=50):
        self.data = data
        self.tasksQuantity = len(self.data)
        self.stepsQuantity = len(self.data[0]) - 1
        self.populationSize = populationSize
        self.pc = pc
        self.pm = pm
        self.generations = generations
        self.populationData = []
        self.bestSolution = []
        self.results = []
        self.FD = []

        self.calculate()
        df = {
            'Population size': self.populationSize,
            'pc': self.pc,
            'pm': self.pm,
            'generations': self.generations,
            'average score': sum(self.results) / self.populationSize,
            'best solution score': min(self.results)
        }
        self.solutionDataFrame = pd.DataFrame(df, index=[0])

    def calculate(self):
        self.generatePopulation()
        self.evaluatePopulation()

        for generation in range(self.generations):
            self.tournamentSelection()
            self.OX()
            self.mutateRandomSwap()
            self.evaluatePopulation()

        self.bestSolution = [el[0] for el in self.populationData[self.results.index(min(self.results))]]

    def generatePopulation(self):
        population = []
        for i in range(self.populationSize):
            listTmp = copy.deepcopy(self.data)
            random.shuffle(listTmp)
            population.append(listTmp)
        self.populationData = population

    def tournamentSelection(self):
        childPopulation = []
        for i in range(self.populationSize):
            sol1, sol2 = random.randrange(self.populationSize), random.randrange(self.populationSize)
            if self.FD[sol1] > self.FD[sol2]:
                childPopulation.append(self.populationData[sol1])
            else:
                childPopulation.append(self.populationData[sol2])
        self.populationData = childPopulation

    def OX(self):
        children = []
        steps = list(range(0, self.populationSize, 2))
        for step in steps:
            if random.random() < self.pc:
                crossingPoint1 = random.randrange(1, len(self.populationData[0]) - 2)
                crossingPoint2 = random.randrange(crossingPoint1 + 1, len(self.populationData[0]) - 1)

                child1mid = self.populationData[step][crossingPoint1:crossingPoint2]
                child1rest = [x for x in self.populationData[step + 1] if x not in child1mid]
                child1 = child1rest[:crossingPoint1] + child1mid + child1rest[crossingPoint1:]

                child2mid = self.populationData[step + 1][crossingPoint1:crossingPoint2]
                child2rest = [x for x in self.populationData[step] if x not in child2mid]
                child2 = child2rest[:crossingPoint1] + child2mid + child2rest[crossingPoint1:]

                children.append(child1)
                children.append(child2)
            else:
                children.append(self.populationData[step])
                children.append(self.populationData[step + 1])
        self.populationData = children

    def mutateRandomSwap(self):
        for sol in range(self.populationSize):
            if random.random() < self.pm:
                swap1, swap2 = random.randrange(self.tasksQuantity), random.randrange(self.tasksQuantity)
                self.populationData[sol][swap1], self.populationData[sol][swap2] = self.populationData[sol][swap2], \
                                                                                   self.populationData[sol][swap1]

    def evaluatePopulation(self):
        self.results = [self.calculateTime(solution) for solution in self.populationData]
        self.FD = [10000 - result for result in self.results]

    def calculateTime(self, inputList):
        listTmp = copy.deepcopy(inputList)
        for column in range(2, self.stepsQuantity + 1):
            listTmp[0][column] += listTmp[0][column - 1]
        for row in range(1, self.tasksQuantity):
            listTmp[row][1] += listTmp[row - 1][1]
        for row in range(1, self.tasksQuantity):
            for column in range(2, self.stepsQuantity + 1):
                listTmp[row][column] += max(listTmp[row - 1][column], listTmp[row][column - 1])
        return listTmp[-1][-1]


class Writer:
    def __init__(self, dataFrame):
        dataFrame.to_csv('dataFile.csv', index=False)
