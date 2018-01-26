import csv
import py.test

__author__ = 'Denis'


@py.test.mark.parametrize("image_dir, expected, result",
                          [("C:\\Users\\Acer\\Desktop\\Asya\\test\\second", "temperature.csv", "result.csv"),
                           ("C:\\Users\\Acer\\Desktop\\Asya\\test\\third", "temperature.csv", "result.csv"),
                           ("C:\\Users\\Acer\\Desktop\\Asya\\test\\fourth", "temperature.csv", "result.csv")])
def test_second_csv_comparable(image_dir, expected, result):
    print(image_dir)
    expected = image_dir + "\\" + expected
    result = image_dir + "\\" + result
    with open(expected, "r", newline='') as expected_file:
        reader = csv.reader(expected_file, delimiter=';')
        expected_table = list(reader)
    with open(result, "r", newline='') as result_file:
        reader = csv.reader(result_file, delimiter=';')
        result_table = list(reader)

    n = len(expected_table)
    if "C" in expected_table[0]:
        col_num = expected_table[0].index("C")
        expected_column = [expected_table[i][col_num] for i in range(1, n)]
        result_column = [result_table[i][2] for i in range(1, n)]
        assert expected_column == result_column

    if "F" in expected_table[0]:
        col_num = expected_table[0].index("F")
        expected_column = [expected_table[i][col_num] for i in range(1, n)]
        result_column = [result_table[i][3] for i in range(1, n)]
        assert expected_column == result_column
