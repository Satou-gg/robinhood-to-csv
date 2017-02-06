# python 3
"""
Purpose of this script is for analytics
http://strftime.org/

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

Unrealized Gain & Loss over time
"""
import json
import dateutil.parser
import operator
import jinja2
from collections import OrderedDict

FILE_NAME = 'robinhood.csv'


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
            self.cumulative_quantity = float(
                dict_obj.get('cumulative_quantity'))
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
        self.created_at_day = self.created_at.strftime("%A")  # Weekday as locale’s full name.	Monday

        self.updated_at_raw = dict_obj.get('updated_at')
        self.updated_at = dateutil.parser.parse(self.updated_at_raw)

        self.updated_at_day = self.updated_at.strftime( "%A")   # Weekday full name.	Monday
        self.updated_at_day_year = self.updated_at.strftime( "%j")  # Day of the year
        self.updated_at_day_number = self.updated_at.strftime( "%d")  # Day of the month as a zero-padded decimal number
        self.updated_at_month = self.updated_at.strftime("%B")  # Month full name.	September
        self.updated_at_month_number = self.updated_at.strftime("%m")  # Month Number
        self.updated_at_year = self.updated_at.strftime("%Y")  # Year with century
        # Hour (24-hour clock) as a zero-padded decimal number
        self.updated_at_hour = self.updated_at.strftime("%H")
        # Week number of the year, Week starts with sunday
        self.updated_at_week = self.updated_at.strftime("%U")

        self.last_transaction_at_raw = dict_obj.get('last_transaction_at')
        self.last_transaction_at = dateutil.parser.parse(
            self.last_transaction_at_raw)


def read_file_into_transaction_objs(filename):
    output = []

    line_count = 1
    first_line = []

    with open(filename) as open_f:
        for line in open_f:
            if line_count == 1:
                first_line_list = line.split(',')
                first_line_list = [current_string.strip()
                                   for current_string in first_line_list]
            else:
                current_line_list = line.split(',')
                current_line_list = [current_string.strip()
                                     for current_string in current_line_list]
                record = dict(zip(first_line_list, current_line_list))

                output.append(record)

            line_count = line_count + 1

    output.sort(key=operator.itemgetter('created_at'))  # Order by date
    # Convert into list of TransactionObjParser
    output = [TransactionObjParser(record) for record in output]
    return output


def print_out(content_list):
    print(json.dumps(content_list, sort_keys=True,
                     indent=4, separators=(',', ': ')))


def summary_table(content_list):
    """
    Summary Json
    """
    summary = OrderedDict()
    transactions = OrderedDict()

    trades_records = []

    for transaction_obj in content_list:
        symbol = transaction_obj.symbol
        side = transaction_obj.side
        state = transaction_obj.state
        quantity = transaction_obj.cumulative_quantity
        price = transaction_obj.price
        updated_day = transaction_obj.updated_at_day
        #
        # print(transaction_obj.created_at)
        # print(transaction_obj.updated_at_day)
        # print('---------------')

        if symbol not in summary:
            summary[symbol] = OrderedDict()
            summary[symbol]['volume'] = 0.0

            summary[symbol]['execs'] = 0
            summary[symbol]['buy_execs'] = 0
            summary[symbol]['sell_execs'] = 0

            summary[symbol]['position'] = 0
            summary[symbol]['gross_value'] = 0

            summary[symbol]['trade_buy_value'] = 0
            summary[symbol]['trade_sell_value'] = 0

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
            summary[symbol]['volume'] = summary[symbol]['volume'] + quantity
            summary[symbol]['trade_volume'] = summary[
                symbol]['trade_volume'] + quantity

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
                summary[symbol]['position'] = summary[
                    symbol]['position'] - quantity
                summary[symbol]['gross_value'] = summary[
                    symbol]['gross_value'] - gross_value

                summary[symbol]['trade_buy_value'] = summary[
                    symbol]['trade_buy_value'] + gross_value

            elif side == 'sell':
                summary[symbol]['sell_execs'] = summary[
                    symbol]['sell_execs'] + 1
                summary[symbol]['position'] = summary[
                    symbol]['position'] + quantity
                summary[symbol]['gross_value'] = summary[
                    symbol]['gross_value'] + gross_value

                summary[symbol]['trade_sell_value'] = summary[
                    symbol]['trade_sell_value'] + gross_value
            else:
                print('error')

            # When the position becames 0 it means that all the brought shares
            # are sold
            if summary[symbol]['position'] == 0.0:
                summary[symbol]['trade'] = summary[symbol]['trade'] + 1
                trade_value = summary[symbol]['gross_value']

                if trade_value < 0:
                    summary[symbol]['cumulative_loss'] = summary[symbol][
                        'cumulative_loss'] + summary[symbol]['gross_value']
                    summary[symbol]['lossing_trades'] = summary[
                        symbol]['lossing_trades'] + 1

                    if summary[symbol]['biggest_losing_trade'] > trade_value:
                        summary[symbol]['biggest_losing_trade'] = trade_value

                    if summary[symbol]['average_lossing_trades']:
                        summary[symbol]['average_lossing_trades'] = (
                            summary[symbol]['average_lossing_trades'] + trade_value) / 2.0
                    else:
                        summary[symbol]['average_lossing_trades'] = trade_value
                else:
                    summary[symbol]['cumulative_gain'] = summary[symbol][
                        'cumulative_gain'] + summary[symbol]['gross_value']
                    summary[symbol]['winning_trades'] = summary[
                        symbol]['winning_trades'] + 1

                    if summary[symbol]['biggest_winning_trade'] < trade_value:
                        summary[symbol]['biggest_winning_trade'] = trade_value

                    if summary[symbol]['average_winning_trades']:
                        summary[symbol]['average_winning_trades'] = (
                            summary[symbol]['average_winning_trades'] + trade_value) / 2.0
                    else:
                        summary[symbol]['average_winning_trades'] = trade_value

                current_trade = OrderedDict()
                current_trade['trade_volume'] = summary[symbol]['trade_volume']
                current_trade['trade_value'] = trade_value
                current_trade['symbol'] = symbol
                current_trade['end_day'] = transaction_obj.updated_at_day
                current_trade[
                    'end_day_of_year'] = transaction_obj.updated_at_day_year

                current_trade[
                    'end_month'] = transaction_obj.updated_at_month_number
                current_trade['end_year'] = transaction_obj.updated_at_year
                current_trade['end_week'] = transaction_obj.updated_at_week
                current_trade['end_hour'] = transaction_obj.updated_at_hour
                current_trade['end_date'] = '{}'.format(
                    transaction_obj.updated_at)

                current_trade['trade_buy_value'] = summary[
                    symbol]['trade_buy_value']
                current_trade['trade_sell_value'] = summary[
                    symbol]['trade_sell_value']
                current_trade['stock_price'] = transaction_obj.price

                current_trade['percent'] = (
                    trade_value / summary[symbol]['trade_buy_value']) * 100

                summary[symbol]['trades'].append(current_trade)
                summary[symbol]['gross_value'] = 0.0
                summary[symbol]['trade_volume'] = 0.0
                summary[symbol]['trade_buy_value'] = 0.0
                summary[symbol]['trade_sell_value'] = 0.0

            if summary[symbol]['position'] == 0 and summary[symbol]['gross_value'] == 0:
                summary[symbol]['open'] = False

                current_sum = 0
                total_trade_buy_value = 0
                total_trade_sell_value = 0

                for current_record in summary[symbol]['trades']:
                    current_sum = current_sum + current_record['trade_value']
                    total_trade_buy_value = total_trade_buy_value + \
                        current_record['trade_buy_value']
                    total_trade_sell_value = total_trade_sell_value + \
                        current_record['trade_sell_value']

                summary[symbol]['net_value'] = current_sum
                summary[symbol]['total_trade_buy_value'] = total_trade_buy_value
                summary[symbol][
                    'total_trade_sell_value'] = total_trade_sell_value
                # TODO: Normization of the percent,  if net_value = 0 does it
                # really add to percent
                summary[symbol]['total_percent'] = (
                    current_sum / total_trade_buy_value) * 100
            else:
                summary[symbol]['open'] = True

    day_year_gain_loss = {
        'day_number_of_year': OrderedDict(),
        'time_in_day': OrderedDict(),
        'year': OrderedDict(),
        'week_number_of_year': OrderedDict(),
        'month': OrderedDict(),
        'hour_of_day': OrderedDict()
    }

    for key in summary:
        trades_list = summary[key]['trades']

        for trade in trades_list:
            trade_value = trade['trade_value']

            # Day of Year
            day_of_year = int(trade['end_day_of_year'])
            if day_of_year not in day_year_gain_loss['day_number_of_year']:
                day_year_gain_loss['day_number_of_year'][
                    day_of_year] = trade_value
            else:
                day_year_gain_loss['day_number_of_year'][day_of_year] = day_year_gain_loss[
                    'day_number_of_year'][day_of_year] + trade_value

            # Week Number
            week_number = int(trade['end_week'])
            if week_number not in day_year_gain_loss['week_number_of_year']:
                day_year_gain_loss['week_number_of_year'][
                    week_number] = trade_value
            else:
                day_year_gain_loss['week_number_of_year'][week_number] = day_year_gain_loss[
                    'week_number_of_year'][week_number] + trade_value

            # Week Number
            hour_of_day = int(trade['end_hour'])
            if hour_of_day not in day_year_gain_loss['hour_of_day']:
                day_year_gain_loss['hour_of_day'][hour_of_day] = trade_value
            else:
                day_year_gain_loss['hour_of_day'][hour_of_day] = day_year_gain_loss[
                    'hour_of_day'][hour_of_day] + trade_value

            # Month Number
            month_string = int(trade['end_month'])
            if month_string not in day_year_gain_loss['month']:
                day_year_gain_loss['month'][month_string] = trade_value
            else:
                day_year_gain_loss['month'][month_string] = day_year_gain_loss[
                    'month'][month_string] + trade_value

    stats = {
        'total_execs': 0,
        'total_buy_execs': 0,
        'total_sell_execs': 0,
        'total_trades': 0,
        'total_winning_trades': 0,
        'total_lossing_trades': 0,

        'total_cumulative_gain': 0,
        'total_cumulative_loss': 0,

        'total_gain_loss': 0,

        'average_winning_trades': None,
        'average_lossing_trades': None
    }
    for key in summary:
        symbol_dict = summary[key]
        #
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

        average_winning_trades = symbol_dict['average_winning_trades']
        average_lossing_trades = symbol_dict['average_lossing_trades']

        # Adding
        stats['total_execs'] = stats['total_execs'] + execs
        stats['total_buy_execs'] = stats['total_buy_execs'] + buy_execs
        stats['total_sell_execs'] = stats['total_sell_execs'] + sell_execs
        stats['total_trades'] = stats['total_trades'] + trade
        stats['total_gain_loss'] = stats['total_gain_loss'] + net_worth

        stats['total_cumulative_gain'] = stats[
            'total_cumulative_gain'] + cumulative_gain
        stats['total_cumulative_loss'] = stats[
            'total_cumulative_loss'] + cumulative_loss

        stats['total_winning_trades'] = stats[
            'total_winning_trades'] + winning_trades
        stats['total_lossing_trades'] = stats[
            'total_lossing_trades'] + lossing_trades

        if average_winning_trades is not None:
            if stats['average_winning_trades']:
                stats['average_winning_trades'] = (stats['average_winning_trades'] + average_winning_trades) / 2.0
            else:
                stats['average_winning_trades'] = average_winning_trades

        if average_lossing_trades is not None:
            if stats['average_lossing_trades']:
                stats['average_lossing_trades'] = (stats['average_lossing_trades'] + average_lossing_trades) / 2.0
            else:
                stats['average_lossing_trades'] = average_lossing_trades

        summary[symbol]['average_winning_trades'] = None
        summary[symbol]['average_lossing_trades'] = None

    output = OrderedDict()
    output['summary'] = summary
    output['transactions'] = transactions
    output['stats'] = stats
    output['day_year_gain_loss'] = day_year_gain_loss

    return output

content_transaction_list = read_file_into_transaction_objs(FILE_NAME)
summary_table_results = summary_table(content_transaction_list)
# print_out(summary_table_results)

templateLoader = jinja2.FileSystemLoader(searchpath="templates")
templateEnv = jinja2.Environment(loader=templateLoader)

templateEnv.filters['sorted'] = sorted

# This constant string specifies the template file we will use.
TEMPLATE_FILE = "index.jinja"

# Read the template file using the environment object.
# This also constructs our Template object.
template = templateEnv.get_template(TEMPLATE_FILE)

# Finally, process the template to produce our final text.
outputText = template.render(summary_table_results)

print(outputText)
