import os


class TxtStrategyLoader:

    def __init__(self, strategy_dir="strategies/txt"):

        self.strategy_dir = strategy_dir

    # ======================================
    # LOAD STRATEGIES
    # ======================================
    def load_strategies(self, strategy_file=None):

        strategies = []

        if not os.path.exists(self.strategy_dir):
            return strategies

        files = []

        # ======================================
        # SPECIFIC STRATEGY
        # ======================================
        if strategy_file:

            files = [strategy_file]

        # ======================================
        # LOAD ALL STRATEGIES
        # ======================================
        else:

            files = os.listdir(self.strategy_dir)

        for file in files:

            if not file.endswith(".txt"):
                continue

            path = os.path.join(
                self.strategy_dir,
                file
            )

            if not os.path.exists(path):
                continue

            strategy = {
                "conditions": []
            }

            with open(path, "r") as f:

                lines = f.readlines()

            in_entry_block = False

            for line in lines:

                line = line.strip()

                if not line:
                    continue

                # ==================================
                # ENTRY BLOCK
                # ==================================
                if line == "ENTRY:":
                    in_entry_block = True
                    continue

                # ==================================
                # CONDITIONS
                # ==================================
                if in_entry_block:

                    if "=" in line:
                        in_entry_block = False

                    else:
                        strategy["conditions"].append(line)
                        continue

                # ==================================
                # KEY=VALUE
                # ==================================
                if "=" in line:

                    key, value = line.split("=", 1)

                    strategy[key.strip()] = value.strip()

            strategies.append(strategy)

        return strategies
