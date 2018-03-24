import numpy as np
import pandas as pd

# 回测函数, asset_value输入标的价格序列，position输入仓位序列，cost输入交易费用
def back_test(asset_value, position, cost):
    w = 0
    strategy_value = [asset_value[0]]
    
    for i in range(len(asset_value)):
        if i == 0:
            strategy_value[0] = strategy_value[0] * (1 - position[i] * cost)
        else:
            daily_return = (asset_value[i] / asset_value[i-1] - 1) * w
            daily_cost = abs(position[i] - position[i-1]) * cost
            strategy_value.append(strategy_value[-1] * (1 + daily_return) * (1 - daily_cost))
        w = position[i]
        
    return strategy_value
   
    
# 将Position序列转换为交易信号[1 - 0 -1]signal序列
def position2signal(position):
    signal = [None] * len(position)
        
    for i in range(len(position)):
        if i == 0:
            if position[i] == 1:
                signal[i] = 1
            else:
                signal[i] = 0
        else:
            if position[i] - position[i-1] == 1:
                signal[i] = 1
            elif position[i] - position[i-1] == -1:
                signal[i] = -1
            else:
                signal[i] = 0
    return signal
    
    
# 指标评价函数，asset_value须包括收盘、最低、最高价，position是0-1信号，period是评价周期
def evaluate_signal(asset_value, strategy_value, signal, position, period):
    strategy_value = np.asarray(strategy_value)
    signal = position2signal(position)
    # 最大不利变动，最大有利变动
    MAE, MFE = [], []
    # 每次交易持有时间，每次盈利利润，每次亏损利润，当日历史最大回撤
    hold_days, profits, losses, drowndown = [], [], [], []
    # 信号发出次数
    signal_amount = 0
    # 回测交易日总数
    test_trading_days = asset_value.shape[0]
    
    for i in range(test_trading_days):
        # 计算MAE，MFE
        if i < test_trading_days - period:
            if signal[i] == 1:
                close = asset_value.close.iloc[i]
                temp = asset_value.iloc[i+1:i+period+1, :]

                Adverse_move = min([temp.low.min()/close - 1, -1e-3])
                Favor_move = max([temp.high.max()/close - 1, 1e-3])

                MAE.append( abs(Adverse_move) )
                MFE.append( Favor_move )
                
        # 计录每次交易持有时间
        if (i == 0 and position[i] == 1) or (i > 0 and position[i-1] == 0 and position[i] == 1):
            hold_days.append(0)
        elif i > 0 and position[i-1] == 1:
            hold_days[-1] += 1
        
        # 记录每次盈利亏损，信号发出次数
        if signal[i] == 1:
            cost = asset_value.close[i]
            signal_amount += 1
        elif signal[i] == -1:
            gain = asset_value.close[i] / cost - 1
            if gain >= 0:
                profits.append(gain)
            else:
                losses.append(-gain)
                
        # 记录当日历史最大回撤
        max_value = max(strategy_value[:i+1])
        drowndown.append( 1 - strategy_value[i]/max_value )
                
                         
    # 计算平均最大不利变动，平均最大有利变动，E比率
    MAE_avg = np.mean(MAE)
    MFE_avg = np.mean(MFE)
    E_ratio = MFE_avg / MAE_avg
    
    # 计算平均每次持有时间，持仓时间占总交易日百分比
    hold_days_avg = np.mean(hold_days)
    hold_pct = sum(hold_days) / test_trading_days
    
    # 计算胜率，盈亏比，最大回撤
    winning_rate = len(profits) / signal_amount
    profit_over_loss = np.mean(profits) / np.mean(losses)
    max_drawndown = max(drowndown)
    
    # 计算年化收益，夏普比率(0.03)
    annual_return = (strategy_value[-1]/strategy_value[0]) ** (243/test_trading_days) - 1
    sharpe = (annual_return - 0.03) / np.std(strategy_value[1:] / strategy_value[:-1]) / np.sqrt(243)
    
    
    ## Report ##
    result = [[annual_return, sharpe, E_ratio, MFE_avg, MAE_avg, test_trading_days, signal_amount, \
        hold_days_avg, hold_pct, winning_rate, profit_over_loss, max_drawndown]]
    columns = ['年化收益率', '夏普比率', 'E比率', '最大有利变动', '最大不利变动', '回测总交易日', '信号发出次数', \
        '平均每笔持仓时间', '持有天数占总交易日百分比', '胜率', '盈亏比', '最大回撤']
    
    result = pd.DataFrame(result, columns=columns)
    return result

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    