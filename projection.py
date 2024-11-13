#!/bin/python3

from sys import argv
from matplotlib import pyplot as plt
import math

class input_vars():
  def __init__(self):
    self.balance = 0.0
    self.monthly_rate = 0.0 # 0.07 / 12 -> 7% PA
    self.monthly_deposit = 0.0
    self.monthly_deposit_yearly_raise = 0.0
    self.max_monthly_deposit = 0.0
    self.yearly_assumed_dividend_percentage = 0.0
    self.num_years = 1
    self.target_amount = 0

    self.show_plot = True

  def sanity_check(self):
    assert self.num_years > 0, 'The number of years must be at least one'
    assert self.max_monthly_deposit >= 0, 'The maximum monthly deposit must be 0 or larger'
    if self.target_amount != 0:
      assert self.num_years == 1

  def get_inputs_from_args(self):
    help_message = '\
      -h --help -> print this message\n\
      -b --balance -> starting balance\n\
      -yr --yearly_rate -> expected growth rate\n\
      -mr --monthly_rate -> same asyr / 12\n\
      -md --monthly_deposit -> monthly contribution to fund\n\
      -mdyr --monthly_deposit_yearly_rise -> how much is contributed more than the previous year per month\n\
      -mdm' '--monthly_deposit_max -> maximum monthly deposit\n\
      -yadp, --yearly_assumed_dividend_percentage -> will show yearly dividend income based on it - quarterly assumed\n\
      -ny --num_years -> duration of the analysis\n\
      -ta --tarrget-amount ->  mutually exclusive with -ny\n\
      -np --no_plot -> don\'t show plot\n'
    if len(argv) == 1:
      print("Running at default parameters")
    elif any(i in argv for i in ['-h', '--help']):
      print(help_message)
      exit()

    i = 1
    while i < len(argv): # why cant python have normal for loops ?
      if argv[i] in ['-b', '--balance']:
        i+=1; self.balance = float(argv[i]) # python doesn't have '++' :(
      elif argv[i] in ['-yr', '--yearly_rate']:
        i+=1; self.monthly_rate = float(argv[i]) / 12
      elif argv[i] in ['-mr', '--monthly_rate']:
        i+=1; self.monthly_rate = float(argv[i])
      elif argv[i] in ['-md', '--monthly_deposit']:
        i+=1; self.monthly_deposit = float(argv[i])
      elif argv[i] in ['-mdyr', '--monthly_deposit_yearly_rise']:
        i+=1; self.monthly_deposit_yearly_raise = float(argv[i])
      elif argv[i] in ['-mdm', '--monthly_deposit_max']:
        i+=1; self.max_monthly_deposit = float(argv[i])
      elif argv[i] in ['-yadp', '-yearly_assumed_dividend_percentage']:
        i+=1; self.yearly_assumed_dividend_percentage = float(argv[i])
      elif argv[i] in ['-ny', '--num_years']:
        i+=1; self.num_years = int(argv[i])
      elif argv[i] in ['-ta', '--target-amount']:
        i+=1; self.target_amount = float(argv[i])
      elif argv[i] in ['-np', '--no_plot']:
        self.show_plot = False
      else:
        assert 0, "'{}' is an invalid option".format(argv[i])
      i+=1

def lerp(a, b, r):
  return a+(b-a)*r

def lerpolated_vals(min_v, max_v, num_v):
  ret_list = []
  if num_v ==0:
    return ret_list
  num_v-=1
  for i in range(num_v+1):
    ret_list.append(lerp(min_v, max_v, i / num_v))
  return ret_list

def show_plot(time_years, balance_history, deposit_history):
  assert len(balance_history) == len(deposit_history) == int(math.ceil(time_years))+1
  years =[i for i in range(int(time_years)+1)]
  if math.ceil(time_years) != math.floor(time_years):
    years.append(time_years)

  plt.plot(years, balance_history, lw=1, color='blue')
  plt.plot(years, deposit_history, lw=1, color='orange')
  labels = ['total balance', 'total deposited']
  plt.legend(labels)

  plt.grid()
  if len(years) < 15:
    plt.hlines(balance_history[:-1], 0, years[:-1], linestyle='--', lw=0.1, color='blue')
    plt.hlines(deposit_history[:-1], 0, years[:-1], linestyle='--', lw=0.1, color='orange')
  plt.hlines(balance_history[-1], 0, years[-1], linestyle='--', lw=0.3, color='blue')
  plt.hlines(deposit_history[-1], 0, years[-1], linestyle='--', lw=0.3, color='orange')

  plt.xlabel('years')
  plt.xticks(years if len(years) < 24 else None)

  if all(i >= 0 for i in deposit_history+balance_history):
    plt.yticks(lerpolated_vals(balance_history[0], balance_history[-1], 8))

  plt.xlim(0, None)

  plt.show()

def main():
  inputs = input_vars()
  inputs.get_inputs_from_args()
  print(vars(inputs))
  inputs.sanity_check()

  total_deposited = 0
  balance_history = []
  deposit_history = []

  i = 0
  while True:
    # yearly
    if i%12 == 0:
      balance_history.append(inputs.balance)
      deposit_history.append(total_deposited)

      if i:
        if inputs.max_monthly_deposit:
          inputs.monthly_deposit = min(inputs.monthly_deposit + inputs.monthly_deposit_yearly_raise, inputs.max_monthly_deposit)
        else:
          inputs.monthly_deposit += inputs.monthly_deposit_yearly_raise
        print('after year {:<3} | total_deposited: {:,.2f} | balance: {:,.2f} | monthly_deposit: {:,.2f} | dividends: {:,.2f}'.format(
              int(i/12), total_deposited, inputs.balance, inputs.monthly_deposit, inputs.yearly_assumed_dividend_percentage * (balance_history[-2] if i >= 24 else 0 + 7.5 * inputs.monthly_deposit) ))

    # monthly
    inputs.balance += inputs.balance * inputs.monthly_rate
    inputs.balance += inputs.monthly_deposit
    total_deposited += inputs.monthly_deposit

    i+=1

    if inputs.target_amount:
      if inputs.balance > inputs.target_amount:
        break
    else:
      if i>=inputs.num_years*12:
        break

  # final
  balance_history.append(inputs.balance)
  deposit_history.append(total_deposited)
  if inputs.target_amount:
    inputs.num_years = i/12
  print('after year {:<3} | total_deposited: {:,.2f} | balance: {:,.2f} | monthly_deposit: {:,.2f}'.format(inputs.num_years, total_deposited, inputs.balance, inputs.monthly_deposit))
  print('balance: {:,.2f}, total_deposited: {:,.2f}, gains: {:,.2f}'.format(inputs.balance, total_deposited, inputs.balance - total_deposited))

  if inputs.show_plot:
    show_plot(inputs.num_years, balance_history, deposit_history)

if __name__ == "__main__":
    main()
