# python 3
# Purpose of this script is to ana
import json
import dateutil.parser
import operator

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
        self.created_at_raw = dict_obj.get('created_at')
        self.created_at = dateutil.parser.parse(self.created_at_raw)
        self.created_at_day = self.created_at.strftime("%A")

        self.updated_at_raw = dict_obj.get('updated_at')
        self.updated_at = dateutil.parser.parse(self.updated_at_raw)
        self.updated_at_day = self.updated_at.strftime("%A")
        self.updated_at_month = self.updated_at.strftime("%B")
        self.updated_at_year = self.updated_at.strftime("%Y")

        self.last_transaction_at_raw = dict_obj.get('last_transaction_at')
        self.last_transaction_at = dateutil.parser.parse(self.last_transaction_at_raw)


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

                output.append(record)

            line_count = line_count + 1

    output.sort(key=operator.itemgetter('created_at'))  # Order by date
    output = [TransactionObjParser(record) for record in output]  # Convert into list of TransactionObjParser
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

    trades_records = []

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

            summary[symbol]['execs'] = 0
            summary[symbol]['buy_execs'] = 0
            summary[symbol]['sell_execs'] = 0

            summary[symbol]['position'] = 0
            summary[symbol]['gross_value'] = 0
            summary[symbol]['net_value'] = 0
            summary[symbol]['trade'] = 0

            summary[symbol]['cumulative_gain'] = 0
            summary[symbol]['cumulative_loss'] = 0

            summary[symbol]['winning_trades'] = 0
            summary[symbol]['lossing_trades'] = 0

            summary[symbol]['biggest_winning_trade'] = 0
            summary[symbol]['biggest_losing_trade'] = 0

            summary[symbol]['average_winning_trades'] = None
            summary[symbol]['average_lossing_trades'] = None

            summary[symbol]['trade_volume'] = 0

            summary[symbol]['win_loss_ratio'] = 0
            summary[symbol]['win_loss_value_ratio'] = 0

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
            summary[symbol]['trade_volume'] = summary[symbol]['trade_volume']  + quantity

            history_string = '{} - {} {} at {:06.3f} (Q:{},P:{})'.format(transaction_obj.created_at,
                                                                         transaction_obj.type.capitalize(),
                                                                         transaction_obj.side.capitalize(),
                                                                         gross_value,
                                                                         quantity,
                                                                         price)
            transactions[symbol].append(history_string)

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

            # When the position becames 0 it means that all the brought shares are sold
            if summary[symbol]['position'] ==  0.0:
                summary[symbol]['trade'] = summary[symbol]['trade'] + 1
                trade_value = summary[symbol]['gross_value']

                if trade_value < 0:
                    summary[symbol]['cumulative_loss'] = summary[symbol]['cumulative_loss'] + summary[symbol]['gross_value']
                    summary[symbol]['lossing_trades'] = summary[symbol]['lossing_trades'] + 1

                    if summary[symbol]['biggest_losing_trade'] > trade_value:
                        summary[symbol]['biggest_losing_trade'] = trade_value

                    if summary[symbol]['average_lossing_trades']:
                        summary[symbol]['average_lossing_trades'] = (summary[symbol]['average_lossing_trades']  + trade_value) / 2.0
                    else:
                        summary[symbol]['average_lossing_trades'] = trade_value
                else:
                    summary[symbol]['cumulative_gain'] = summary[symbol]['cumulative_gain'] + summary[symbol]['gross_value']
                    summary[symbol]['winning_trades'] = summary[symbol]['winning_trades'] + 1

                    if summary[symbol]['biggest_winning_trade'] < trade_value:
                        summary[symbol]['biggest_winning_trade'] = trade_value

                    if summary[symbol]['average_winning_trades']:
                        summary[symbol]['average_winning_trades'] = (summary[symbol]['average_winning_trades']  + trade_value) / 2.0
                    else:
                        summary[symbol]['average_winning_trades'] = trade_value


                current_trade = {}
                current_trade['trade_volume'] = summary[symbol]['trade_volume']
                current_trade['trade_value'] = trade_value
                current_trade['end_day'] =  transaction_obj.updated_at_day
                current_trade['end_date'] =  '{}'.format(transaction_obj.updated_at)

                summary[symbol]['trades'].append(current_trade)
                summary[symbol]['gross_value'] = 0.0
                summary[symbol]['trade_volume'] = 0.0

            if summary[symbol]['position'] == 0 and summary[symbol]['gross_value'] == 0:
                summary[symbol]['open'] = False

                current_sum = 0
                for current_record in summary[symbol]['trades']:
                    current_trade_value = current_record['trade_value']
                    current_sum = current_sum + current_trade_value
                summary[symbol]['net_value'] = current_sum
            else:
                summary[symbol]['open'] = True

    stats = {
        'total_execs': 0,
        'total_buy_execs': 0,
        'total_sell_execs': 0,
        'total_trades': 0,
        'total_winning_trades':0,
        'total_lossing_trades':0,

        'total_cumulative_gain':0,
        'total_cumulative_loss':0,

        'total_gain_loss': 0 ,
    }
    for key in summary:
        symbol_dict = summary[key]

        execs = symbol_dict['execs']
        buy_execs = symbol_dict['buy_execs']
        sell_execs = symbol_dict['sell_execs']

        trade = symbol_dict['trade']
        volume = symbol_dict['volume']
        net_worth = symbol_dict['net_value']

        cumulative_gain = symbol_dict['cumulative_gain']
        cumulative_loss = symbol_dict['cumulative_loss']

        lossing_trades = symbol_dict['lossing_trades']
        winning_trades = symbol_dict['winning_trades']

        # Adding
        stats['total_execs'] = stats['total_execs'] + execs
        stats['total_buy_execs'] = stats['total_buy_execs'] + buy_execs
        stats['total_sell_execs'] = stats['total_sell_execs'] + sell_execs
        stats['total_trades'] = stats['total_trades'] + trade
        stats['total_gain_loss'] = stats['total_gain_loss'] + net_worth

        stats['total_cumulative_gain'] = stats['total_cumulative_gain'] + cumulative_gain
        stats['total_cumulative_loss'] = stats['total_cumulative_loss'] + cumulative_loss

        stats['total_winning_trades'] = stats['total_winning_trades'] + winning_trades
        stats['total_lossing_trades'] = stats['total_lossing_trades'] + lossing_trades

    output = {}
    output['summary'] = summary
    output['transactions'] = transactions
    output['stats'] = stats
    return output

content_transaction_list = read_file_into_transaction_objs(fname)
summary_table_results = summary_table(content_transaction_list)
print_out(summary_table_results)
