/*Вариант №19
В базе данных домашнего бюджета хранятся сведения о ежедневных тратах по
статьям расходов.
Структура входного файла in.txt
Дата Статья Раздел Сумма
15.05 Продукты Черный_хлеб 25
15.05 Транспорт Автобус 30
16.05 Продукты Молоко 45
...
Сформировать список трат по статье «Продукты», упорядочив по разделам
Структура выходного файла out.txt
Дата Раздел Сумма
15.05 Молоко 25
16.05 Черный_хлеб 45
*/
#include <stdio.h>
#include <string.h>

#define MAX 100

struct Expense {
    char date[10];
    char article[20];
    char section[50];
    int amount;
};

void sortBySection(struct Expense *arr, int n) {
    struct Expense temp;
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (strcmp(arr[j].section, arr[j+1].section) > 0) {
                temp = arr[j];
                arr[j] = arr[j+1];
                arr[j+1] = temp;
            }
        }
    }
}

int main() {
    struct Expense data[MAX];
    int count = 0;

    FILE *in = fopen("in.txt", "r");
    while (fscanf(in, "%s %s %s %d",
                  data[count].date,
                  data[count].article,
                  data[count].section,
                  &data[count].amount) == 4) {
        if (strcmp(data[count].article, "Продукты") == 0) {
            count++;
        }
    }

    sortBySection(data, count);

    FILE *out = fopen("out.txt", "w");
    for (int i = 0; i < count; i++) {
        fprintf(out, "%s %s %d\n",
                data[i].date,
                data[i].section,
                data[i].amount);
    }

    fclose(out);
    fclose(in);
    return 0;
}
