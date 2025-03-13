import pandas as pd

def row_to_text(row) -> str:
    text = ""
    for col_name, value in row.items():
        text += f"{col_name}: {value} \n"
        # print(col_name + ": " + value)
        # break
    return text

def excel_to_text_list(path) -> list[str]:
    data = pd.read_excel(path)
    texts = []
    for _, row in data.iterrows():
        text = row_to_text(row)
        texts.append(text)
    return texts

if __name__ == "__main__":
    print(excel_to_text_list(path="./documentation-helper/data/init.xlsx"))