# 设置控制台编码为UTF-8
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import json
import re
import argparse
import urllib.request
import urllib.error
import ssl
import sqlite3
from datetime import datetime


def get_skill_dir() -> str:
    """获取技能安装目录"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_db_path() -> str:
    """获取数据库文件路径"""
    config_dir = os.path.join(get_skill_dir(), "config")
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, "stock_quote.db")


def get_output_path(filename: str) -> str:
    """
    获取输出文件的完整路径
    规则: 所有输出文件保存到当前工作目录，而不是技能安装目录
    """
    return os.path.join(os.getcwd(), filename)


def get_stock_type(stock_code: str) -> str:
    """
    判断股票代码类型
    返回: A股(上海), A股(深圳), 港股, 美股
    """
    if stock_code.startswith('6') or stock_code.startswith('5'):
        return 'sh'
    elif stock_code.startswith('0') or stock_code.startswith('3'):
        return 'sz'
    elif stock_code.startswith('8') or stock_code.startswith('4'):
        return 'bj'
    elif stock_code.isdigit() and len(stock_code) == 5:
        return 'hk'
    else:
        return 'unknown'


def fetch_a_stock(symbol: str) -> dict:
    """
    获取A股实时行情 - 使用新浪财经API
    """
    stock_type = get_stock_type(symbol)
    
    if stock_type == 'sh':
        query = f'sh{symbol}'
    elif stock_type == 'sz':
        query = f'sz{symbol}'
    else:
        return {'error': f'不支持的股票类型: {symbol}'}
    
    url = f'https://hq.sinajs.cn/list={query}'
    
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(url, headers={
            'Referer': 'https://finance.sina.com.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
            content = response.read().decode('gb2312', errors='ignore')
        
        pattern = f'var hq_str_{query}="([^"]*)"'
        match = re.search(pattern, content)
        
        if not match:
            return {'error': f'未找到股票数据: {symbol}'}
        
        data = match.group(1).split(',')
        
        if len(data) < 32:
            return {'error': f'数据不完整: {symbol}'}
        
        current = float(data[3]) if data[3] else None
        close = float(data[2]) if data[2] else None
        
        change = None
        pct_change = None
        if current and close:
            change = current - close
            pct_change = (change / close) * 100
        
        return {
            'symbol': symbol,
            'name': data[0],
            'open': float(data[1]) if data[1] else None,
            'close': close,
            'current': current,
            'high': float(data[4]) if data[4] else None,
            'low': float(data[5]) if data[5] else None,
            'volume': float(data[8]) if data[8] else None,
            'amount': float(data[9]) if data[9] else None,
            'change': change,
            'pct_change': pct_change,
            'date': data[30],
            'time': data[31],
            'market': 'A股'
        }
        
    except Exception as e:
        return {'error': f'获取失败: {str(e)}'}


def fetch_hk_stock(symbol: str) -> dict:
    """
    获取港股实时行情 - 使用新浪财经API
    """
    url = f'https://hq.sinajs.cn/list=hk{symbol}'
    
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(url, headers={
            'Referer': 'https://finance.sina.com.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
            content = response.read().decode('gb2312', errors='ignore')
        
        pattern = f'var hq_str_hk{symbol}="([^"]*)"'
        match = re.search(pattern, content)
        
        if not match:
            return {'error': f'未找到港股数据: {symbol}'}
        
        data = match.group(1).split(',')
        
        if len(data) < 10:
            return {'error': f'港股数据不完整: {symbol}'}
        
        current = float(data[3]) if data[3].replace('.','').isdigit() else None
        close = float(data[6]) if data[6].replace('.','').isdigit() else None
        change = float(data[7]) if data[7].replace('.','').replace('-','').isdigit() else None
        pct_change = float(data[8]) if data[8].replace('.','').replace('-','').isdigit() else None
        
        return {
            'symbol': symbol,
            'name': data[1],
            'open': float(data[2]) if data[2].replace('.','').isdigit() else None,
            'current': current,
            'high': float(data[4]) if data[4].replace('.','').isdigit() else None,
            'low': float(data[5]) if data[5].replace('.','').isdigit() else None,
            'close': close,
            'change': change,
            'pct_change': pct_change,
            'volume': float(data[12]) if data[12].replace('.','').isdigit() else None,
            'amount': float(data[11]) if data[11].replace('.','').isdigit() else None,
            'date': data[17],
            'time': data[18],
            'market': '港股'
        }
        
    except Exception as e:
        return {'error': f'获取港股失败: {str(e)}'}


def fetch_us_stock(symbol: str) -> dict:
    """
    获取美股实时行情 - 使用新浪财经API
    """
    url = f'https://hq.sinajs.cn/list=n_{symbol}'
    
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(url, headers={
            'Referer': 'https://finance.sina.com.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
            content = response.read().decode('gb2312', errors='ignore')
        
        pattern = f'var hq_str_n_{symbol}="([^"]*)"'
        match = re.search(pattern, content)
        
        if not match:
            return {'error': f'未找到美股数据: {symbol}'}
        
        data = match.group(1).split(',')
        
        if len(data) < 10:
            return {'error': f'美股数据不完整: {symbol}'}
        
        current = float(data[0]) if data[0] else None
        open_price = float(data[1]) if data[1] else None
        
        change = float(data[2]) if data[2] else None
        pct_change = float(data[3]) if data[3] else None
        
        return {
            'symbol': symbol,
            'name': data[0],
            'current': current,
            'open': open_price,
            'change': change,
            'pct_change': pct_change,
            'high': float(data[4]) if data[4] else None,
            'low': float(data[5]) if data[5] else None,
            'volume': float(data[6]) if data[6] else None,
            'market': '美股'
        }
        
    except Exception as e:
        return {'error': f'获取美股失败: {str(e)}'}


def fetch_stock(symbol: str, market: str | None = None) -> dict:
    """
    获取股票行情主函数
    market: 指定市场类型 'a', 'hk', 'us', 'auto'(自动识别)
    """
    symbol = symbol.strip().upper()
    
    if market == 'a' or market == 'auto' or market is None:
        if len(symbol) == 6 and symbol.isdigit():
            return fetch_a_stock(symbol)
    
    if market == 'hk' or market == 'auto' or market is None:
        if len(symbol) == 5 and symbol.isdigit():
            return fetch_hk_stock(symbol)
    
    if market == 'us' or market == 'auto' or market is None:
        if len(symbol) <= 5 and symbol.isalpha():
            return fetch_us_stock(symbol)
    
    return {'error': f'无法识别股票代码: {symbol}, 市场: {market}'}


def format_stock_info(data: dict) -> str:
    """格式化股票信息为可读字符串"""
    if 'error' in data:
        return f"错误: {data['error']}"
    
    lines = []
    lines.append(f"{'='*50}")
    lines.append(f"股票: {data.get('symbol')} - {data.get('name', 'N/A')}")
    lines.append(f"市场: {data.get('market', 'N/A')}")
    lines.append(f"{'='*50}")
    
    if data.get('current') is not None:
        lines.append(f"当前价格: {data['current']}")
    
    if data.get('open') is not None:
        lines.append(f"开盘价: {data['open']}")
    
    if data.get('close') is not None:
        lines.append(f"昨收价: {data['close']}")
    
    if data.get('high') is not None:
        lines.append(f"最高价: {data['high']}")
    
    if data.get('low') is not None:
        lines.append(f"最低价: {data['low']}")
    
    if data.get('change') is not None:
        lines.append(f"涨跌额: {data['change']:.2f}")
    
    if data.get('pct_change') is not None:
        pct = data['pct_change']
        sign = '+' if pct > 0 else ''
        lines.append(f"涨跌幅: {sign}{pct:.2f}%")
    
    if data.get('volume') is not None:
        vol = data['volume']
        if vol >= 100000000:
            lines.append(f"成交量: {vol/100000000:.2f}亿")
        elif vol >= 10000:
            lines.append(f"成交量: {vol/10000:.2f}万")
        else:
            lines.append(f"成交量: {vol}")
    
    if data.get('amount') is not None:
        amount = data['amount']
        if amount >= 100000000:
            lines.append(f"成交额: {amount/100000000:.2f}亿")
        elif amount >= 10000:
            lines.append(f"成交额: {amount/10000:.2f}万")
        else:
            lines.append(f"成交额: {amount}")
    
    if data.get('date'):
        lines.append(f"日期: {data['date']}")
    if data.get('time'):
        lines.append(f"时间: {data['time']}")
    
    lines.append(f"{'='*50}")
    
    return '\n'.join(lines)


def save_to_json(data: dict, output_file: str):
    """保存数据到JSON文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"数据已保存到: {output_file}")


def init_db():
    """初始化数据库表"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            name TEXT,
            market TEXT,
            current REAL,
            open REAL,
            close REAL,
            high REAL,
            low REAL,
            change REAL,
            pct_change REAL,
            volume REAL,
            amount REAL,
            query_time TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_symbol_time ON stock_history(symbol, query_time)
    ''')
    conn.commit()
    conn.close()


def save_to_db(data: dict):
    """保存股票数据到SQLite数据库"""
    if 'error' in data:
        return
    
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO stock_history 
        (symbol, name, market, current, open, close, high, low, change, pct_change, volume, amount, query_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('symbol'),
        data.get('name'),
        data.get('market'),
        data.get('current'),
        data.get('open'),
        data.get('close'),
        data.get('high'),
        data.get('low'),
        data.get('change'),
        data.get('pct_change'),
        data.get('volume'),
        data.get('amount'),
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    
    conn.commit()
    conn.close()
    print(f"数据已保存到数据库: {db_path}")


def main():
    parser = argparse.ArgumentParser(
        description='实时股票行情查询工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python main.py 600519              # 查询A股上证指数(自动保存到数据库)
  python main.py 000001              # 查询A股平安银行
  python main.py 00700               # 查询港股腾讯控股
  python main.py 600519 -m a         # 指定查询A股
  python main.py 600519 -o result.json  # 保存到JSON文件
  python main.py 600519 000001 600036  # 批量查询多只股票
        '''
    )
    
    parser.add_argument('symbols', nargs='+', help='股票代码')
    parser.add_argument('-m', '--market', choices=['a', 'hk', 'us', 'auto'], 
                        default='auto', help='指定市场类型 (默认: auto)')
    parser.add_argument('-o', '--output', help='输出JSON文件路径')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细信息')
    
    args = parser.parse_args()
    
    init_db()
    
    results = []
    
    for symbol in args.symbols:
        if args.verbose:
            print(f"正在查询: {symbol}...")
        
        data = fetch_stock(symbol, args.market)
        print(format_stock_info(data))
        
        if 'error' not in data:
            save_to_db(data)
        
        results.append(data)
    
    if len(results) == 1:
        final_data = results[0]
    else:
        final_data = {'stocks': results, 'query_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    if args.output:
        save_to_json(final_data, args.output)


if __name__ == '__main__':
    main()
