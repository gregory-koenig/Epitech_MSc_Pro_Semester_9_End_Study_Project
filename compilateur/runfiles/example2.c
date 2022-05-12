#include <stdio.h>

void show_arr(int* arr)
{
    for (int i = 0; i <= sizeof(&arr) / sizeof(int); ++i)
    {
        printf("%d\n", arr[i]);
    }
}

int main()
{
    int arr[3];
    arr[0] = 0;
    arr[1] = 2;
    arr[2] = 4;
    show_arr(&arr[0]);
    printf("test\n");
    return 0;
}
