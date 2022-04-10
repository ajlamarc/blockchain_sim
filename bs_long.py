import random
import numpy as np


class BlockchainSimulator:
    def __init__(self):
        self.Fn = random.randint(20, 200)
        self.F1 = random.randint(5, 50)
        self.Ch = []
        self.Cn = 0
        for i in range(self.Fn):
            Ci = random.randint(0, 4)
            self.Ch.append(Ci)
            self.Cn += Ci

        self.FnO = round(0.1 * self.Fn)
        self.FnY = self.Fn - self.FnO
        self.F1Y = round(0.1 * self.F1)
        self.F1O = self.F1 - self.F1Y
        self.On = 2 * self.FnO + self.F1O
        self.Yn = 2 * self.FnY + self.F1Y

        self.pediatricTotalCost = 0
        self.youngTotalCost = 0
        self.oldTotalCost = 0

        self.clockp = 0  # time of next pediatric event, initially 0
        self.clocky = 0  # time for next young event, initially 0
        self.clocko = 0  # time for next older adult event, initially 0

        # events have 3 types: clinical visit, outpatient procedure, and surgery
        # varying costs and probabilities
        self.ptype = -1  # type of next pediatric event
        self.ytype = -1  # type of next young event (age under 65)
        self.otype = -1  # type of next old event

        # these will be used along with exponential distribution, to set clocks
        self.mu1 = (200 / self.Cn) * 2  # average time to next pediatric event
        self.mu2 = (50 / self.Yn) * 9  # average time to next young event
        self.mu3 = (50 / self.On) * 6  # average time to next older adult event

        # clinical visit, outpatient procedure, and inpatient procedure respectively
        # clinical visit is most likely and cheapest, inpatient the opposite
        self.lowCosts = [60, 1000, 3000]
        self.highCosts = [200, 10000, 100000]
        self.probabilities = [0.90, 0.07, 0.03]
        self.indices = [0, 1, 2]

        # multipliers for young and pediatric: young typically cheaper, pediatric more expensive
        self.youngCostMult = 0.75
        self.pediatricCostMult = 1.5

        print("Number of children: " + str(self.Cn))
        print("Number of young adults: " + str(self.Yn))
        print("Number of old adults: " + str(self.On))
        print()

    def generate_next_care_event_pediatric(self):
        # use mu1 to determine date and type, update clockp and ptype
        self.clockp = self.clockp + round(np.random.exponential(self.mu1))
        self.ptype = np.random.choice(self.indices, p=self.probabilities)
        return

    def generate_next_care_event_young(self):
        # mu2, clocky and ytype
        self.clocky = self.clocky + round(np.random.exponential(self.mu2))
        self.ytype = np.random.choice(self.indices, p=self.probabilities)
        return

    def generate_next_care_event_old(self):
        # mu3, clocko and otype
        self.clocko = self.clocko + round(np.random.exponential(self.mu3))
        self.otype = np.random.choice(self.indices, p=self.probabilities)
        return

    def process_event(self, eventType):
        if eventType == 0:  # pediatric
            low = self.lowCosts[self.ptype]
            high = self.highCosts[self.ptype]
            self.pediatricTotalCost += round(random.randint(low, high)
                                             * self.pediatricCostMult)
        elif eventType == 1:  # young
            low = self.lowCosts[self.ytype]
            high = self.highCosts[self.ytype]
            self.youngTotalCost += round(random.randint(low,
                                         high) * self.youngCostMult)
        else:  # old
            low = self.lowCosts[self.otype]
            high = self.highCosts[self.otype]
            self.oldTotalCost += random.randint(low, high)
        return

    def clear_events_and_costs(self):
        self.clockp = 0
        self.clocky = 0
        self.clocko = 0

        self.ptype = -1
        self.ytype = -1
        self.otype = -1

        self.pediatricTotalCost = 0
        self.youngTotalCost = 0
        self.oldTotalCost = 0


def main():
    # Definitions of all variables
    # Definition of constant, for instance the path and name of the file containing the values of the variables.
    # data structure for the simulator. Mainly clocks, events and an event list

    bs = BlockchainSimulator()
    #Y = random.randint(5, 20)
    lastYearTotalCost = -1
    simTradPremium = 0
    simSmartPremium = 0
    for y in range(1, 1000):
        day = 0

        # Calculate traditional premiums for year y() Family and individual
        olderAdultPremium = 800 * 12  # assume avg 800 / mo for older adults
        youngAdultPremium = 400 * 12
        pediatricPremium = 200 * 12

        totalTraditionalPremium = (bs.On * olderAdultPremium) + \
            (bs.Yn * youngAdultPremium) + (bs.Cn * pediatricPremium)

        # Calculate smart contract premiums for year y(SPT_Surplus[y-1]) Families and individuals, considering savings by last year’s surplus.
        totalSmartContractPremium = -1
        if (y == 1):  # first year, use traditional premium number as the number to collect
            totalSmartContractPremium = totalTraditionalPremium
        else:  # after first year, use expenses for last year and replenish missing funds with premiums
            totalSmartContractPremium = lastYearTotalCost

        bs.clear_events_and_costs()  # make sure queue has all zero entries
        bs.generate_next_care_event_pediatric()
        bs.generate_next_care_event_young()
        bs.generate_next_care_event_old()

        while day < 365:
            # get event happening soonest
            day = min(bs.clockp, bs.clocko, bs.clocky)

            if bs.clockp == day & day < 365:
                bs.process_event(0)  # process pediatric event
                bs.generate_next_care_event_pediatric()
            if bs.clocky == day & day < 365:
                bs.process_event(1)  # process young event
                bs.generate_next_care_event_young()
            if bs.clocko == day & day < 365:
                bs.process_event(2)  # process old event
                bs.generate_next_care_event_old()

        totalCost = bs.pediatricTotalCost + bs.youngTotalCost + bs.oldTotalCost
        lastYearTotalCost = totalCost
        simTradPremium += totalTraditionalPremium
        simSmartPremium += totalSmartContractPremium

    print("Total traditional premiums per year: " + str(simTradPremium / 1000))
    print("Total smart contract premiums per year: " +
          str(simSmartPremium / 1000))
    print("Smart contract savings: " +
          str((simTradPremium - simSmartPremium) * 100 / simTradPremium) + " %")


main()
