import os
import psycopg
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), "pass.env")
load_dotenv(env_path)

# SQLに接続する基礎設定
conn = psycopg.connect(
    host="localhost",
    port=5432,
    dbname="inquiry_system",
    user="postgres",
    password=os.getenv("DB_PASSWORD"))

print("PostgreSQLに接続できました")


# メニュー表示
while True:
    print()
    print("========================")
    print("問い合わせ管理システム")
    print("========================")

    print("1. 問い合わせ一覧")
    print("2. 問い合わせ検索")
    print("3. 新規問い合わせ登録")
    print("4. 処理状況の変更")
    print("5. 問い合わせ集計")
    print("6. 終了")

    menu = input("番号を入力してください：")

    print("選択した番号：", menu)

    # 1. 問い合わせ一覧
    if menu == "1":
        print("問い合わせ一覧を表示します")

        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT * FROM inquiries
                ORDER BY id ASC;
                """)
            rows = cur.fetchall()

            for row in rows:
                print(row)

    # 2. 問い合わせ検索
    elif menu == "2":
        
        print("問い合わせを検索します")
        print()
        print("1.問い合わせID")
        print("2.処理状況")
        print("3.キーワード検索")
        
        while True:
            confirm = input("上記検索方法の中から指定の数字を入力してください：")
            if confirm.isdigit():
                confirm = int(confirm)
                if confirm in [1,2,3]:
                    break
            print("1~3の数字を入力してください")

        if confirm == 1:
            while True:
                inquiry_id = input("問い合わせIDを入力してください：")

                if inquiry_id.isdigit():
                    inquiry_id = int(inquiry_id)
                    break
                print("数字を入力してください")
                
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM inquiries WHERE id = %s;",
                    (inquiry_id,))
                inquiry = cur.fetchone()

            if inquiry is None:
                print("問い合わせが見つかりませんでした")
            else:
                print(inquiry)
        if confirm ==2:
            print("処理状況を選択してください")
            print()
            print("1.未対応")
            print("2.対応中")
            print("3.対応済")
            while True:
                status_choice = input("番号を入力してください：")
                if status_choice.isdigit():
                    status_choice = int(status_choice)
                    if status_choice in [1,2,3]:
                        break
                print("1~3の数字を入力してください")
            if status_choice == 1:
                status = "未対応"
            elif status_choice == 2:
                status = "対応中"
            else:
                status = "対応済"
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM inquiries WHERE status = %s;",
                            (status,))
                inquiries = cur.fetchall()
            if not inquiries:
                print("該当する問い合わせがありませんでした")
            else:
                for inquiry in inquiries:
                    print(inquiry)
        elif confirm == 3:
            print("1.キーワードのみの検索")
            print("2.キーワード+処理状況の検索")

            while True:
                status_choice = input("番号を入力してください：")

                if status_choice.isdigit():
                    status_choice = int(status_choice)

                    if status_choice in [1, 2]:
                        break

                print("1または2を選択してください")

            if status_choice == 1:
                keyword = input("検索するキーワードを入力してください：")

                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT * FROM inquiries WHERE inquiry_content LIKE %s;",
                        (f"%{keyword}%",))
                    inquiries = cur.fetchall()

            elif status_choice == 2:
                print("1.未対応")
                print("2.対応中")
                print("3.対応済")

                while True:
                    status_choice = input("番号を入力してください：")

                    if status_choice.isdigit():
                        status_choice = int(status_choice)

                        if status_choice in [1, 2, 3]:
                            break

                    print("1~3の数字を入力してください")

                if status_choice == 1:
                    status = "未対応"
                elif status_choice == 2:
                    status = "対応中"
                else:
                    status = "対応済"

                keyword = input("検索するキーワードを入力してください：")

                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT * FROM inquiries WHERE status = %s AND inquiry_content LIKE %s;",
                        (status, f"%{keyword}%"))
                    inquiries = cur.fetchall()

            if not inquiries:
                print("該当する問い合わせがありませんでした")
            else:
                for inquiry in inquiries:
                    print(inquiry)
        

    # 新規問い合わせ登録
    elif menu == "3":
        print("新規問い合わせを登録します")

        while True:
            inquiry_id = input("新規の問い合わせIDを入力してください：")
            if inquiry_id.isdigit():
                inquiry_id = int(inquiry_id)
                break
            print("数字を入力してください")


        employee_name = input("登録する氏名を入力してください：")
        department = input("登録する部署を入力してください：")
        inquiry_content = input("登録する問い合わせ内容を入力してください：")

        # 問い合わせIDが既に存在するか確認
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM inquiries WHERE id = %s;",
                (inquiry_id,))
            existing = cur.fetchone()

        # 既存データがある場合
        if existing is not None:
            print()
            print("この問い合わせIDは既に登録されています。")
            print("===== 既存のデータ =====")
            print("問い合わせID：", existing[0])
            print("氏名：", existing[1])
            print("部署：", existing[2])
            print("問い合わせ内容：", existing[3])
            print("処理状況：", existing[4])
            print("登録日：", existing[5])

            while True:
                print()
                print("このデータを上書きしますか？")
                print("1. はい")
                print("2. いいえ")

                confirm = input("番号を入力してください：")

                if confirm == "1":
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            UPDATE inquiries
                            SET employee_name = %s,
                                department = %s,
                                inquiry_content = %s
                            WHERE id = %s;
                            """,
                            (
                                employee_name,
                                department,
                                inquiry_content,
                                inquiry_id))

                    conn.commit()
                    print("問い合わせを上書きしました")
                    break

                elif confirm == "2":
                    print("上書きをキャンセルしました")
                    break

                else:
                    print("正しい番号を入力してください")

        # 既存データがない場合
        else:
            print()
            print("===== 登録内容の確認 =====")
            print("問い合わせID：", inquiry_id)
            print("氏名：", employee_name)
            print("部署：", department)
            print("問い合わせ内容：", inquiry_content)
            print("処理状況：未対応")

            while True:
                print()
                print("この内容で登録しますか？")
                print("1. はい")
                print("2. いいえ")

                confirm = input("番号を入力してください：")

                if confirm == "1":
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            INSERT INTO inquiries
                            (id, employee_name, department,
                             inquiry_content, status, created_at)
                            VALUES (%s, %s, %s, %s, %s, CURRENT_DATE);
                            """,
                            (
                                inquiry_id,
                                employee_name,
                                department,
                                inquiry_content,
                                "未対応"))

                    conn.commit()
                    print("問い合わせを登録しました")
                    break

                elif confirm == "2":
                    print("登録をキャンセルしました")
                    break

                else:
                    print("正しい番号を入力してください")

    # 4. 処理状況・問い合わせ内容の変更
    elif menu == "4":
        print("問い合わせ内容の変更をします")

        while True:
            inquiry_id = input("変更する問い合わせIDを入力してください：")
            if inquiry_id.isdigit():
                inquiry_id = int(inquiry_id)
                break
            print("数字を入力してください")
                          

        # 現在の登録内容を取得
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM inquiries WHERE id = %s;",
                (inquiry_id,))
            inquiry = cur.fetchone()

        if inquiry is None:
            print("該当する問い合わせがありません。")

        else:
            print()
            print("===== 現在の登録内容 =====")
            print("問い合わせID：", inquiry[0])
            print("氏名：", inquiry[1])
            print("部署：", inquiry[2])
            print("問い合わせ内容：", inquiry[3])
            print("処理状況：", inquiry[4])
            print("登録日：", inquiry[5])

            while True:
                print()
                print("変更する項目を選択してください")
                print("1. 氏名")
                print("2. 部署")
                print("3. 問い合わせ内容")
                print("4. 処理状況")
                print("5. キャンセル")

                change = input("番号を入力してください：")

                # 氏名の変更
                if change == "1":
                    new_value = input("新しい氏名を入力してください：")

                    print()
                    print("===== 変更内容の確認 =====")
                    print("変更前：", inquiry[1])
                    print("変更後：", new_value)

                    while True:
                        print()
                        print("この内容で変更しますか？")
                        print("1. 変更する")
                        print("2. 変更しない")

                        confirm = input("番号を入力してください：")

                        if confirm == "1":
                            with conn.cursor() as cur:
                                cur.execute(
                                    """
                                    UPDATE inquiries
                                    SET employee_name = %s
                                    WHERE id = %s;
                                    """,
                                    (new_value, inquiry_id))

                            conn.commit()
                            print("氏名を変更しました。")
                            break

                        elif confirm == "2":
                            print("変更をキャンセルしました。")
                            break

                        else:
                            print("正しい番号を入力してください")

                    if confirm == "1" or confirm == "2":
                        break

                # 部署の変更
                elif change == "2":
                    new_value = input("新しい部署を入力してください：")

                    print()
                    print("===== 変更内容の確認 =====")
                    print("変更前：", inquiry[2])
                    print("変更後：", new_value)

                    while True:
                        print()
                        print("この内容で変更しますか？")
                        print("1. 変更する")
                        print("2. 変更しない")

                        confirm = input("番号を入力してください：")

                        if confirm == "1":
                            with conn.cursor() as cur:
                                cur.execute(
                                    """
                                    UPDATE inquiries
                                    SET department = %s
                                    WHERE id = %s;
                                    """,
                                    (new_value, inquiry_id)
                                )

                            conn.commit()
                            print("部署を変更しました。")
                            break

                        elif confirm == "2":
                            print("変更をキャンセルしました。")
                            break

                        else:
                            print("正しい番号を入力してください")

                    if confirm == "1" or confirm == "2":
                        break

                # 問い合わせ内容の変更
                elif change == "3":
                    new_value = input("新しい問い合わせ内容を入力してください：")

                    print()
                    print("===== 変更内容の確認 =====")
                    print("変更前：", inquiry[3])
                    print("変更後：", new_value)

                    while True:
                        print()
                        print("この内容で変更しますか？")
                        print("1. 変更する")
                        print("2. 変更しない")

                        confirm = input("番号を入力してください：")

                        if confirm == "1":
                            with conn.cursor() as cur:
                                cur.execute(
                                    """
                                    UPDATE inquiries
                                    SET inquiry_content = %s
                                    WHERE id = %s;
                                    """,
                                    (new_value, inquiry_id))

                            conn.commit()
                            print("問い合わせ内容を変更しました。")
                            break

                        elif confirm == "2":
                            print("変更をキャンセルしました。")
                            break

                        else:
                            print("正しい番号を入力してください")

                    if confirm == "1" or confirm == "2":
                        break

                # 処理状況の変更
                elif change == "4":
                    print()
                    print("新しい処理状況を選択してください")
                    print("1. 未対応")
                    print("2. 対応中")
                    print("3. 対応済")

                    while True:
                        status_choice = input("番号を入力してください：")

                        if status_choice == "1":
                            new_status = "未対応"
                            break

                        elif status_choice == "2":
                            new_status = "対応中"
                            break

                        elif status_choice == "3":
                            new_status = "対応済"
                            break

                        else:
                            print("正しい番号を入力してください")

                    print()
                    print("===== 変更内容の確認 =====")
                    print("変更前：", inquiry[4])
                    print("変更後：", new_status)

                    while True:
                        print()
                        print("この内容で変更しますか？")
                        print("1. 変更する")
                        print("2. 変更しない")

                        confirm = input("番号を入力してください：")

                        if confirm == "1":
                            with conn.cursor() as cur:
                                cur.execute(
                                    """
                                    UPDATE inquiries
                                    SET status = %s
                                    WHERE id = %s;
                                    """,
                                    (new_status, inquiry_id))

                            conn.commit()
                            print("処理状況を変更しました。")
                            break

                        elif confirm == "2":
                            print("変更をキャンセルしました。")
                            break

                        else:
                            print("正しい番号を入力してください")

                    if confirm == "1" or confirm == "2":
                        break

                # キャンセル
                elif change == "5":
                    print("変更をキャンセルしました")
                    break

                else:
                    print("正しい番号を入力してください")

    # 5. 問い合わせ集計
    elif menu == "5":
        print("問い合わせを集計します")

        
        with conn.cursor() as cur:
            cur.execute(
            "SELECT COUNT(*) FROM inquiries;")
            count = cur.fetchone()

            cur.execute(
            "SELECT status, COUNT(*) FROM inquiries GROUP BY status;")
            status_counts = cur.fetchall()
        print("==================")
        print("　問い合わせ集計　")
        print("==================")
        print("問い合わせ件数：", count[0],"件")
        print()
        print("[処理状況別の件数]")
        for status, number in status_counts:
            print(status, "：", number, "件")


    # 6. 終了
    elif menu == "6":
        print("システムを終了します")
        break

    else:
        print("正しい番号を入力してください")


# データベース接続を閉じる
conn.close()