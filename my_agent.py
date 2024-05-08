from agt_server.agents.base_agents.lsvm_agent import MyLSVMAgent
from agt_server.local_games.lsvm_arena import LSVMArena
from agt_server.agents.test_agents.lsvm.min_bidder.my_agent import MinBidAgent
from agt_server.agents.test_agents.lsvm.jump_bidder.jump_bidder import JumpBidder
from agt_server.agents.test_agents.lsvm.truthful_bidder.my_agent import TruthfulBidder
import time
import os
import random
import gzip
import json
from path_utils import path_from_local_root
import numpy as np


NAME = "Mr.ROBOTO"


class MyAgent(MyLSVMAgent):
    def setup(self):
        # TODO: Fill out with anything you want to initialize each auction
        self.abandoned = []

    def calculate_c_score(self, regional, C):
        if regional == True:
            return 1 + 160 / (100 * (1 + np.exp(4 - C)))
        else:
            return 1 + 320 / (100 * (1 + np.exp(10 - C)))

    def abandon(self, prices, valuations, good):
        # Prev_Utility = 0
        # for good in valuations.keys():
        #     if (not good in self.abandoned) and not (valuations[good] == 0):
        #         Prev_Utility += valuations[good] - prices[good]
        # Prev_Utility *= self.get_current_CScore(regional, valuations)
        # new_valuations = valuations
        # new_valuations[good] = 0
        # New_utility = 0
        # for good in new_valuations.keys():
        #     if (not good in self.abandoned) and not (new_valuations[good] == 0):
        #         New_utility += valuations[good] - prices[good]
        # New_utility *= self.get_current_CScore(regional, new_valuations)

        # if New_utility > Prev_Utility:
        #     return True
        # else:
        #     return False
        if valuations[good] * self.CScore < prices[good]:
            return True
        else:
            return False

    def national_bidder_strategy(self):
        # TODO: Fill out with your national bidder strategy
        pass

    def regional_bidder_strategy(self):
        # TODO: Fill out with your regional bidder strategy
        pass

    def get_both_bids(self):
        prices = self.get_min_bids()
        valuations = self.get_valuations()
        allocated = self.get_tentative_allocation()
        bids = {}
        # with open("output.txt", "w") as output:
        #     output.write(str(valuations))

        # We should have a strict rule for abandoning on a good
        abandoned_goods = []
        for good in valuations.keys():
            if self.abandon(prices, valuations, good):
                abandoned_goods.append(good)

        # Only abandon one good max
        for good in abandoned_goods:
            if not (good in self.abandoned):
                self.abandoned.append(good)

        for good in valuations.keys():
            if not (
                (good in self.abandoned)
                or (good in allocated)
                or (valuations[good] == 0)
            ):
                # TO-DO: currently increasing by 10 percent
                bids[good] = self.clip_bid(good, prices[good] * 1.1)
                print(
                    f"I bid on good {good} with price {bids[good]} with my valuation {valuations[good]}, current_price {prices[good]} and my csore {self.CScore}."
                    f"should I abandon? {self.abandon(prices, valuations, good)}"
                )

        return bids

    def get_bids(self):
        # if self.get_current_round() == 1:
        #     print("We got in........")
        valuations = self.get_valuations()
        self.C = 0
        for good in valuations.keys():
            if not (valuations[good] == 0) and not (good in self.abandoned):
                self.C += 1
        self.regional = True
        if self.is_national_bidder():
            self.regional = False
        self.CScore = self.calculate_c_score(self.regional, self.C)

        # if self.is_national_bidder():
        #     return self.national_bidder_strategy()
        # else:
        #     return self.regional_bidder_strategy()

        return self.get_both_bids()

    def update(self):
        # TODO: Fill out with anything you want to update each round
        # self.CScore = self.calculate_c_score(self.regional, self.C)
        # print(f"self.CSore is {self.CScore}, self.C is {self.C}.")
        pass

    def teardown(self):
        # TODO: Fill out with anything you want to run at the end of each auction
        pass


################### SUBMISSION #####################
my_agent_submission = MyAgent(NAME)
####################################################


def process_saved_game(filepath):
    """
    Here is some example code to load in a saved game in the format of a json.gz and to work with it
    """
    print(f"Processing: {filepath}")

    # NOTE: Data is a dictionary mapping
    with gzip.open(filepath, "rt", encoding="UTF-8") as f:
        game_data = json.load(f)
        for agent, agent_data in game_data.items():
            if agent_data["valuations"] is not None:
                # agent is the name of the agent whose data is being processed
                agent = agent

                # bid_history is the bidding history of the agent as a list of maps from good to bid
                bid_history = agent_data["bid_history"]

                # price_history is the price history of the agent as a list of maps from good to price
                price_history = agent_data["price_history"]

                # util_history is the history of the agent's previous utilities
                util_history = agent_data["util_history"]

                # util_history is the history of the previous tentative winners of all goods as a list of maps from good to winner
                winner_history = agent_data["winner_history"]

                # elo is the agent's elo as a string
                elo = agent_data["elo"]

                # is_national_bidder is a boolean indicating whether or not the agent is a national bidder in this game
                is_national_bidder = agent_data["is_national_bidder"]

                # valuations is the valuations the agent recieved for each good as a map from good to valuation
                valuations = agent_data["valuations"]

                # regional_good is the regional good assigned to the agent
                # This is None in the case that the bidder is a national bidder
                regional_good = agent_data["regional_good"]

            # TODO: If you are planning on learning from previously saved games enter your code below.


def process_saved_dir(dirpath):
    """
    Here is some example code to load in all saved game in the format of a json.gz in a directory and to work with it
    """
    for filename in os.listdir(dirpath):
        if filename.endswith(".json.gz"):
            filepath = os.path.join(dirpath, filename)
            process_saved_game(filepath)


if __name__ == "__main__":

    # Heres an example of how to process a singular file
    # process_saved_game(path_from_local_root("saved_games/2024-04-08_17-36-34.json.gz"))
    # or every file in a directory
    # process_saved_dir(path_from_local_root("saved_games"))

    ### DO NOT TOUCH THIS #####
    agent = MyAgent(NAME)
    arena = LSVMArena(
        num_cycles_per_player=1,
        timeout=1,
        local_save_path="saved_games",
        players=[
            agent,
            MyAgent("CP - MyAgent"),
            MyAgent("CP2 - MyAgent"),
            # MyAgent("CP3 - MyAgent"),
            MinBidAgent("Min Bidder"),
            JumpBidder("Jump Bidder"),
            TruthfulBidder("Truthful Bidder"),
        ],
    )

    start = time.time()
    arena.run()
    end = time.time()
    print(f"{end - start} Seconds Elapsed")
