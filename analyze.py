# python 3
# Purpose of this script is to ana
import json

fname = 'robinhood.csv'


class TransactionObjParser(object):

    def __init__(self, dict_obj):
        """
        Parse Object
        """
        self.symbol = dict_obj.get('symbol')
        self.state = dict_obj.get('state')
        # Can be queued/ canncelled/ filled
        self.side = dict_obj.get('side')
        # Can be sell, buy

        self.type = dict_obj.get('type')
        self.time_in_force = dict_obj.get('time_in_force')
        self.tigger = dict_obj.get('tigger')
        self.extended_hours = bool(dict_obj.get('extended_hours'))

        try:
            self.quantity = float(dict_obj.get('quantity'))
        except:
            self.quantity = None

        try:
            self.cumulative_quantity = float(dict_obj.get('cumulative_quantity'))
        except:
            self.cumulative_quantity = None

        try:
            self.price = float(dict_obj.get('price'))
        except:
            self.price = None

        try:
            self.fees = float(dict_obj.get('fees'))
        except:
            self.fees = None

        try:
            self.stop_price = float(dict_obj.get('stop_price'))
        except:
            self.stop_price = None

        try:
            self.average_price = float(dict_obj.get('average_price'))
        except:
            self.average_price = None

        # last_transaction_at, updated_at, created_at
        self.created_at = dict_obj.get('created_at')
        self.updated_at = dict_obj.get('updated_at')
        self.last_transaction_at = dict_obj.get('last_transaction_at')


def read_file_into_transaction_objs(filename):
    output = []

    line_count = 1
    first_line = []

    with open(filename) as open_f:
        for line in open_f:
            if line_count == 1:
                first_line_list = line.split(',')
                first_line_list = [current_string.strip() for current_string in first_line_list]
            else:
                current_line_list = line.split(',')
                current_line_list = [current_string.strip() for current_string in current_line_list]
                record = dict(zip(first_line_list, current_line_list))

                #print(record)
                output.append(TransactionObjParser(record))

            line_count = line_count + 1
        return output


def print_out(content_list):
    print(json.dumps(content_list,sort_keys=True, indent=4, separators=(',', ': ')))


def summary_table(content_list):
    """
    Total trades
    Total volume

    { 'symbol': {'volume': }}

    Trade Distribution by Price
    Performance by Price
    Distribution by Volume Traded
    Performance by Volume Traded

    Performance by Symbol - Top 20
    Performance by Symbol - Bottom 20

    Win/Loss Ratio

    Performace by Year (Aggregate Gain & Loss / Per-trade Average)
    Performace by Month (Aggregate Gain & Loss / Per-trade Average)
    Performance by Week (Aggregate Gain & Loss / Per-trade Average)
    Performance by Day of Month (Aggregate Gain & Loss / Per-trade Average)

    Performance by Hour of Day

    Trade Distribution by Year/ Month/ Week/ Day of Month

    Trade Distribution by Duration (Intraday/ Multiday)
    Performance by Duration (Intraday/ Multiday)

    Total gain/loss:
    Average winning trade:
    Average losing trade:
    Total number of trades:
    Total Number of winning trades:
    Total Number of losing trades:

    Largest gain
    Largest loss

    Cumulative Gain & Loss over time





    """
    output = {'summary':{},
              'transactions':{}}

    for transaction_obj in content_list:
        symbol = transaction_obj.symbol
        side = transaction_obj.side
        state = transaction_obj.state
        quantity =  transaction_obj.cumulative_quantity
        price =  transaction_obj.price

        if symbol not in output['summary']:
            output['summary'][symbol] = {}
            output['summary'][symbol]['volume'] = 0.0
            output['summary'][symbol]['buy_execs'] = 0
            output['summary'][symbol]['execs'] = 0
            output['summary'][symbol]['sell_execs'] = 0
            output['summary'][symbol]['position'] = 0
            output['summary'][symbol]['gross_value'] = 0
            output['summary'][symbol]['net_worth'] = 0
            output['summary'][symbol]['trade'] = 0
            output['summary'][symbol]['winning_trades'] = 0
            output['summary'][symbol]['lossing_trades'] = 0

            output['summary'][symbol]['trades'] = []
            output['transactions'][symbol] = []

        ignore_line = True

        if state == 'filled':
            ignore_line = False

        if state == 'cancelled' and transaction_obj.average_price is not None:
            ignore_line = False

        if ignore_line is False:
            gross_value = quantity * price
            output['summary'][symbol]['volume'] = output['summary'][symbol]['volume']  + quantity

            history_string = '{} {} at {:06.3f} ({})'.format(transaction_obj.type.capitalize(), transaction_obj.side.capitalize(), gross_value, quantity)
            output['transactions'][symbol].append(history_string)
            # print(side)
            # if symbol == 'THLD' and output['summary'][symbol]['position'] >= 0:
            #      print(dict_obj)
            output['summary'][symbol]['execs'] = output['summary'][symbol]['execs'] + 1

            if side == 'buy':
                output['summary'][symbol]['buy_execs'] = output['summary'][symbol]['buy_execs'] + 1
                output['summary'][symbol]['position'] = output['summary'][symbol]['position'] - quantity
                output['summary'][symbol]['gross_value'] = output['summary'][symbol]['gross_value'] - gross_value
            elif side == 'sell':
                output['summary'][symbol]['sell_execs'] = output['summary'][symbol]['sell_execs'] + 1
                output['summary'][symbol]['position'] = output['summary'][symbol]['position'] + quantity
                output['summary'][symbol]['gross_value'] = output['summary'][symbol]['gross_value'] + gross_value
            else:
                print('error')

            if output['summary'][symbol]['position'] ==  0.0:
                output['summary'][symbol]['trade'] = output['summary'][symbol]['trade'] + 1
                trade_value = output['summary'][symbol]['gross_value']

                if trade_value <= 0:
                    output['summary'][symbol]['lossing_trades'] = output['summary'][symbol]['lossing_trades'] + 1
                else:
                    output['summary'][symbol]['winning_trades'] = output['summary'][symbol]['winning_trades'] + 1

                output['summary'][symbol]['trades'].append(trade_value)
                output['summary'][symbol]['gross_value'] = 0.0

            if output['summary'][symbol]['position'] == 0 and output['summary'][symbol]['gross_value'] == 0:
                output['summary'][symbol]['open'] = False
                output['summary'][symbol]['net_worth'] = sum(output['summary'][symbol]['trades'])
            else:
                output['summary'][symbol]['open'] = True

    return output

content_transaction_list = read_file_into_transaction_objs(fname)
summary_table_results = summary_table(content_transaction_list)
print_out(summary_table_results)
