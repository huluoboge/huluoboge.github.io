#!/usr/bin/env python3
"""
Table to CSV Converter
将特定格式的表格数据转换为CSV格式
"""

import csv


def parse_table_file(file_path):
    """解析表格文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 移除空行和换行符
    lines = [line.strip() for line in lines if line.strip()]
    
    print(f"总行数: {len(lines)}")
    print("前10行内容:")
    for i in range(min(10, len(lines))):
        print(f"{i}: {lines[i]}")
    
    # 表头是前7行（因为"Similarity to origin"占两行）
    headers = [
        "Title",
        "Authors", 
        "Year",
        "Citations",
        "References",
        "Similarity to origin"
    ]
    
    # 数据从第7行开始（索引7，因为"to origin"占了一行）
    data_rows = []
    
    # 每6行组成一个完整的记录
    for i in range(7, len(lines), 6):
        if i + 5 < len(lines):
            row = [
                lines[i],      # Title
                lines[i+1],    # Authors
                lines[i+2],    # Year
                lines[i+3],    # Citations
                lines[i+4],    # References
                lines[i+5]     # Similarity to origin
            ]
            data_rows.append(row)
        else:
            print(f"警告: 第{i}行开始的数据不完整")
    
    return headers, data_rows


def save_to_csv(headers, data_rows, output_file):
    """保存为CSV文件"""
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        
        # 写入表头
        writer.writerow(headers)
        
        # 写入数据
        for row in data_rows:
            writer.writerow(row)
    
    print(f"CSV文件已保存至: {output_file}")


def main():
    """主函数"""
    input_file = "table.md"
    output_file = "table_data.csv"
    
    print(f"正在解析表格文件: {input_file}")
    
    headers, data_rows = parse_table_file(input_file)
    
    if headers and data_rows:
        print(f"成功解析 {len(data_rows)} 行数据")
        print(f"表头: {headers}")
        
        save_to_csv(headers, data_rows, output_file)
        
        # 显示前几行数据作为预览
        print("\n数据预览:")
        print(f"{headers}")
        for i, row in enumerate(data_rows[:3]):
            print(f"{row}")
            if i >= 2:
                print("...")
                break
    else:
        print("解析失败，请检查表格格式")


if __name__ == "__main__":
    main()
