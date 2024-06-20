import re

import pandas as pd
import streamlit as st  # streamlitのimport

from problem import CarGroupProblem


# 追加
def sanitize_filename(filename):
    """Sanitize the uploaded file name to prevent directory traversal attacks"""
    return re.sub(r"[^a-zA-Z0-9_.-]", "_", filename)


# 追加
def validate_data(df, required_columns):
    """Validate the data to ensure required columns are present"""
    return all(column in df.columns for column in required_columns)


# 追加
def clean_data(df):
    """Basic data cleaning"""
    df = df.dropna()  # Remove missing values
    df = df.applymap(
        lambda x: x.strip() if isinstance(x, str) else x
    )  # Trim whitespace
    return df


def preprocess(students, cars):
    """UploadedFile(csv) -> pd.DataFrame"""
    # validationチェックを追加
    try:
        students_df = pd.read_csv(students)
        cars_df = pd.read_csv(cars)
    except Exception as e:
        st.error(f"Error reading CSV files: {e}")
        return None, None

    if not validate_data(students_df, ["student_id", "license", "gender", "grade"]):
        st.error("Invalid students data")
        return None, None

    if not validate_data(cars_df, ["car_id", "capacity"]):
        st.error("Invalid cars data")
        return None, None

    students_df = clean_data(students_df)
    cars_df = clean_data(cars_df)

    return students_df, cars_df


def convert_to_csv(df):
    """pd.DataFrame -> csv"""
    return df.to_csv(index=False).encode("utf-8")


# 画面を二分割する（画面の左側をファイルアップロード、右側を最適化結果の表示とする）
# col1: 左側、col2: 右側
col1, col2 = st.columns(2)

# 画面の左側の実装
with col1:
    # ファイルアップロードのフィールド
    students_file = st.file_uploader("学生データ", type="csv")
    cars_file = st.file_uploader("車データ", type="csv")

    # 全てのデータがアップロードされたら以降のUIを表示（studentsとcarsはファイルアップロードがされていない場合はNoneとなり、以下UIの表示はしない）
    if students_file is not None and cars_file is not None:
        # ファイル名をサニタイズ
        students_filename = sanitize_filename(students_file.name)
        cars_filename = sanitize_filename(cars_file.name)

        # 最適化ボタンの表示
        if st.button("最適化を実行"):
            try:
                # 最適化ボタンが押されたら最適化を実行
                # 前処理（データ読み込み）
                students_df, cars_df = preprocess(students_file, cars_file)

                if students_df is not None and cars_df is not None:
                    # 最適化実行
                    solution_df = CarGroupProblem(students_df, cars_df).solve()
                    # 画面の右側にダウンロードボタンと最適化結果を表示する
                    # 追加：最適化結果が帰ってきたら表示する
                    if solution_df is not None:
                        with col2:
                            st.write("#### 最適化結果")
                            # ダウンロードボタンの表示
                            csv = convert_to_csv(solution_df)
                            st.download_button(
                                "Press to Download",
                                csv,
                                "solution.csv",
                                "text/csv",
                                key="download-csv",
                            )
                            # 最適化結果の表示
                            st.write(solution_df)
                    else:
                        st.error("Optimization failed")
                else:
                    st.error("Data validation failed.")
            except Exception as e:
                st.error(f"An error occurred during data loading: {e}")
