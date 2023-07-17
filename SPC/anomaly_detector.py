# ripped from https://github.com/omerfarukozturk/AnomalyDetection
# minor modifications made
import pandas as pd

class AnomalyDetector:
    def __init__(self, series):
        self.data = pd.DataFrame(series.rename('amount'))
        self.mean = series.mean()
        self.sigma = series.std()

    # Rule 1: One point is more than 3 standard deviations from the mean (outlier)
    def rule1(self):

        def isBetween(value, lower, upper):
            isBetween = value < upper and value > lower
            return 0 if isBetween else 1

        upperLimit = self.mean + 3 * self.sigma
        lowerLimit = self.mean - 3 * self.sigma

        self.data['Rule1'] = self.data.apply(lambda row: isBetween(row['amount'], lowerLimit, upperLimit), axis=1)

    # Rule 2: Nine (or more) points in a row are on the same
    # side of the mean (shift)
    def rule2(self):
        values = [0] * len(self.data)

        # +1 means upside, -1 means downside
        upsideOrDownside = 0
        count = 0
        for i in range(len(self.data)):
            amount = self.data.iloc[i]['amount']
            if amount > self.mean:
                if upsideOrDownside == 1:
                    count += 1
                else:
                    upsideOrDownside = 1
                    count = 1
            elif amount < self.mean:
                if upsideOrDownside == -1:
                    count += 1
                else:
                    upsideOrDownside = -1
                    count = 1

            if count >= 9:
                values[i] = 2

        self.data['Rule2'] = values

        # Rule 3: Six (or more) points in a row are continually
        # increasing (or decreasing) (trend)

    def rule3(self):
        values = [0] * len(self.data)

        previousAmount = self.data.iloc[0]['amount']
        # +1 means increasing, -1 means decreasing
        increasingOrDecreasing = 0
        count = 0
        for i in range(1, len(self.data)):
            amount = self.data.iloc[i]['amount']
            if amount > previousAmount:
                if increasingOrDecreasing == 1:
                    count += 1
                else:
                    increasingOrDecreasing = 1
                    count = 1
            elif amount < previousAmount:
                if increasingOrDecreasing == -1:
                    count += 1
                else:
                    increasingOrDecreasing = -1
                    count = 1

            if count >= 6:
                values[i] = 3

            previousAmount = amount

        self.data['Rule3'] = values

        # Rule 4: Fourteen (or more) points in a row alternate in direction,
        # increasing then decreasing (bimodal, 2 or more factors in data set)

    def rule4(self):
        values = [0] * len(self.data)

        previousAmount = self.data.iloc[0]['amount']
        # +1 means increasing, -1 means decreasing
        bimodal = 0
        count = 1
        for i in range(1, len(self.data)):
            amount = self.data.iloc[i]['amount']

            if amount > previousAmount:
                bimodal += 1
                if abs(bimodal) != 1:
                    count = 0
                    bimodal = 0
                else:
                    count += 1
            elif amount < previousAmount:
                bimodal -= 1
                if abs(bimodal) != 1:
                    count = 0
                    bimodal = 0
                else:
                    count += 1

            previousAmount = amount

            if count >= 14:
                values[i] = 4

        self.data['Rule4'] = values

        # Rule 5: Two (or three) out of three points in a row are more than
        # 2 standard deviations from the mean in the same direction (shift)

    def rule5(self):
        if len(self.data) < 3: return

        values = [0] * len(self.data)
        upperLimit = self.mean - 2 * self.sigma
        lowerLimit = self.mean + 2 * self.sigma

        for i in range(len(self.data) - 3):
            first = self.data.iloc[i]['amount']
            second = self.data.iloc[i + 1]['amount']
            third = self.data.iloc[i + 2]['amount']

            setValue = False
            validCount = 0
            if first > self.mean and second > self.mean and third > self.mean:
                validCount += 1 if first > lowerLimit else 0
                validCount += 1 if second > lowerLimit else 0
                validCount += 1 if third > lowerLimit else 0
                setValue = validCount >= 2
            elif first < self.mean and second < self.mean and third < self.mean:
                validCount += 1 if first < upperLimit else 0
                validCount += 1 if second < upperLimit else 0
                validCount += 1 if third < upperLimit else 0
                setValue = validCount >= 2

            if setValue:
                values[i + 2] = 5

        self.data['Rule5'] = values

    # Rule 6: Four (or five) out of five points in a row are more than 1
    # standard deviation from the mean in the same direction (shift or trend)
    def rule6(self):
        if len(self.data) < 5: return

        values = [0] * len(self.data)
        upperLimit = self.mean - self.sigma
        lowerLimit = self.mean + self.sigma

        for i in range(len(self.data) - 5):
            pVals = list(map(lambda x: self.data.iloc[x]['amount'], range(i, i + 5)))

            setValue = False
            if len(list(filter(lambda x: x > self.mean, pVals))) == 5:
                setValue = len(list(filter(lambda x: x > lowerLimit, pVals))) >= 4
            elif len(list(filter(lambda x: x < self.mean, pVals))) == 5:
                setValue = len(list(filter(lambda x: x < upperLimit, pVals))) >= 4

            if setValue:
                values[i + 4] = 6

        self.data['Rule6'] = values

    # Rule 7: Fifteen points in a row are all within 1 standard deviation of the mean
    # on either side of the mean (reduced variation or measurement issue)
    def rule7(self):
        if len(self.data) < 15: return
        values = [0] * len(self.data)
        upperLimit = self.mean + self.sigma
        lowerLimit = self.mean - self.sigma

        for i in range(len(self.data) - 15):
            setValue = True
            for y in range(15):
                item = self.data.iloc[i + y]['amount']
                if item >= upperLimit or item <= lowerLimit:
                    setValue = False
                    break

            if setValue:
                values[i + 14] = 7

        self.data['Rule7'] = values

    # Rule 8: Eight points in a row exist with none within 1 standard deviation of the mean
    # and the points are in both directions from the mean (bimodal, 2 or more factors in data set)
    def rule8(self):
        if len(self.data) < 8: return
        values = [0] * len(self.data)

        for i in range(len(self.data) - 8):
            setValue = True
            for y in range(8):
                item = self.data.iloc[i + y]['amount']
                if abs(self.mean - item) < self.sigma:
                    setValue = False
                    break

            if setValue:
                values[i + 8] = 8

        self.data['Rule8'] = values

    def apply_rules(self, rules):
        for i in rules:
            eval(f'self.rule{i}()')

    def violations(self):
        df = self.data[self.data.columns[1:]]
        df = df.loc[df.sum(axis=1) > 0]
        df['violations'] = [list(filter(lambda x: bool(x), i)) for i in df.values]
        return df.violations
