from google import genai
import json
import os

client = genai.Client()

def main():
    print("AIプログラミングレッスンメーカー")
    lang = input("言語を入力 >")
    print(f"言語: {lang}で作成を開始します....\nファイル構造を作成しています....")
    responce_1 = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="あなたは経験豊富かつ優秀なプログラミングの講師です。これから" + lang + "（プログラミング言語）についての実際にプログラミングして勉強できるデジタル教材を作成してもらいます。初心者が基本をマスターできるレベルをゴールとし、学習者が挫折しないよう最適な章の構成を考え、各章に分けてファイルの名前と拡張子を.で区切った文字列を「filename」キーに（ファイル名と拡張子の区切り以外にピリオドを用いてはいけません。）、どのような内容にするかを書いた指示（指示のみ出力し、本文は出力しない）を「config」キーに入れ出力してください。それ以外は出力しないでください。もし言語がプログラミング言語ではなければERRORと返してください。",
        config={
            "response_mime_type": "application/json"
        }
    )
    if (responce_1.text == "ERROR"):
        print("ファイルの作成に失敗しました。\n予想される問題: >言語がプログラミング言語ではない</n強制終了します....")
        exit()
    
    response_text = responce_1.text

    start_index = response_text.find('[')
    end_index = response_text.rfind(']')

    json_text = response_text[start_index:end_index+1]
    chapters = json.loads(json_text)

    file_number = 1

    os.makedirs("lessons", exist_ok=True)
    for chapter in chapters:
        filename = os.path.splitext(chapter["filename"])[1]
        file_path = os.path.join("lessons", str(file_number) + filename)
        with open(file_path, "w", encoding = "utf-8") as f:
            f.write(chapter["config"])
        print(f"作成が完了しました: {file_path}\n{file_number}個目のファイルを作成しました")
        file_number += 1

    print("ファイル構成を作成しました。ファイルの内容を作成します。\nこの作業には時間がかかります。少々お待ち下さい....")

    for i in range(1, file_number):
        extension = os.path.splitext(chapters[i-1]["filename"])[1]
        file_path = os.path.join("lessons", str(i) + extension)
        
        with open(file_path, "r", encoding = "utf-8") as f:
            instruction = f.read()

        responce_2 = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"あなたは経験豊富かつ優秀なプログラミングの講師です。以下の指示に従って、プログラミングレッスンの内容（コードや説明文）を作成してください。なお、ファイル名は{file_path}です。ファイルの拡張子を加味して作成してください。\n\n指示:\n{instruction}",
            config={
                "response_mime_type": "text/plain"
            }
        )
        with open(file_path, "w", encoding = "utf-8") as f:
            f.write(responce_2.text)
        print(f"作成が完了しました: {file_path}\n{i}個目のファイルの内容を作成しました")

if __name__ == "__main__":
    main()