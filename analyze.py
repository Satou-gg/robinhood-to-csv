# python 3
# Purpose of this script is to ana
import json
import dateutil.parser

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
        self.created_at_obj = dateutil.parser.parse(self.created_at)
        self.created_at_day = self.created_at_obj.strftime("%A")

        self.updated_at = dict_obj.get('updated_at')
        self.updated_at_obj = dateutil.parser.parse(self.updated_at)
        self.updated_at_day = self.updated_at_obj.strftime("%A")

        self.last_transaction_at = dict_obj.get('last_transaction_at')
        self.last_transaction_at_obj = dateutil.parser.parse(self.last_transaction_at)


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

    Trade Distribution by Price
    Performance by Price
    Distribution by Volume Traded
    Performance by Volume Traded

    Performance by Symbol - Top 20
    Performance by Symbol - Bottom 20

    Win/Loss Ratio

    Performance by Year (Aggregate Gain & Loss / Per-trade Average)
    Performance by Month (Aggregate Gain & Loss / Per-trade Average)
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
    summary = {}
    transactions = {}

    for transaction_obj in content_list:
        symbol = transaction_obj.symbol
        side = transaction_obj.side
        state = transaction_obj.state
        quantity =  transaction_obj.cumulative_quantity
        price =  transaction_obj.price
        updated_day = transaction_obj.updated_at_day
        #
        # print(transaction_obj.created_at)
        # print(transaction_obj.updated_at_day)
        # print('---------------')

        if symbol not in summary:
            summary[symbol] = {}
            summary[symbol]['volume'] = 0.0
            summary[symbol]['buy_execs'] = 0
            summary[symbol]['execs'] = 0
            summary[symbol]['sell_execs'] = 0
            summary[symbol]['position'] = 0
            summary[symbol]['gross_value'] = 0
            summary[symbol]['net_worth'] = 0
            summary[symbol]['trade'] = 0
            summary[symbol]['winning_trades'] = 0
            summary[symbol]['lossing_trades'] = 0

            summary[symbol]['trades'] = []
            transactions[symbol] = []

        ignore_line = True

        if state == 'filled':
            ignore_line = False

        if state == 'cancelled' and transaction_obj.average_price is not None:
            ignore_line = False

        if ignore_line is False:
            gross_value = quantity * price
            summary[symbol]['volume'] = summary[symbol]['volume']  + quantity

            history_string = '{} - {} {} at {:06.3f} (Q:{},P:{})'.format(transaction_obj.created_at, transaction_obj.type.capitalize(), transaction_obj.side.capitalize(), gross_value, quantity, price)
            transactions[symbol].append(history_string)
            # print(side)
            # if symbol == 'THLD' and summary[symbol]['position'] >= 0:
            #      print(dict_obj)
            summary[symbol]['execs'] = summary[symbol]['execs'] + 1

            if side == 'buy':
                summary[symbol]['buy_execs'] = summary[symbol]['buy_execs'] + 1
                summary[symbol]['position'] = summary[symbol]['position'] - quantity
                summary[symbol]['gross_value'] = summary[symbol]['gross_value'] - gross_value
            elif side == 'sell':
                summary[symbol]['sell_execs'] = summary[symbol]['sell_execs'] + 1
                summary[symbol]['position'] = summary[symbol]['position'] + quantity
                summary[symbol]['gross_value'] = summary[symbol]['gross_value'] + gross_value
            else:
                print('error')

            if summary[symbol]['position'] ==  0.0:
                summary[symbol]['trade'] = summary[symbol]['trade'] + 1
                trade_value = summary[symbol]['gross_value']

                if trade_value < 0:
                    summary[symbol]['lossing_trades'] = summary[symbol]['lossing_trades'] + 1
                else:
                    summary[symbol]['winning_trades'] = summary[symbol]['winning_trades'] + 1

                summary[symbol]['trades'].append(trade_value)
                summary[symbol]['gross_value'] = 0.0

            if summary[symbol]['position'] == 0 and summary[symbol]['gross_value'] == 0:
                summary[symbol]['open'] = False
                summary[symbol]['net_worth'] = sum(summary[symbol]['trades'])
            else:
                summary[symbol]['open'] = True

    stats = {
        'total_execs': 0,
        'total_buy_execs': 0,
        'total_sell_execs': 0,
        'total_trades': 0,
        'total_winning_trades':0,
        'total_lossing_trades':0,
        'total_gain_loss': 0 ,
    }
    for key in summary:
        symbol_dict = summary[key]

        execs = symbol_dict['execs']
        buy_execs = symbol_dict['buy_execs']
        sell_execs = symbol_dict['sell_execs']
        lossing_trades = symbol_dict['lossing_trades']
        winning_trades = symbol_dict['winning_trades']
        trade = symbol_dict['trade']
        volume = symbol_dict['volume']
        net_worth = symbol_dict['net_worth']

        # Adding
        stats['total_execs'] = stats['total_execs'] + execs
        stats['total_buy_execs'] = stats['total_buy_execs'] + buy_execs
        stats['total_sell_execs'] = stats['total_sell_execs'] + sell_execs
        stats['total_trades'] = stats['total_trades'] + trade
        stats['total_gain_loss'] = stats['total_gain_loss'] + net_worth

    output = {}
    output['summary'] = summary
    output['transactions'] = transactions
    output['stats'] = stats
    return output

content_transaction_list = read_file_into_transaction_objs(fname)
summary_table_results = summary_table(content_transaction_list)
print_out(summary_table_results)
