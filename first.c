#include <stdio.h>
int main() {
    int sum = 0, i = 1;     // 初始化变量[7,8](@ref)
    while(i <= 100) {       // 循环条件判断[7](@ref)
        sum += i;
        i++;                // 手动更新计数器[8](@ref)
    }
    printf("结果为：%d\n", sum);
    return 0;
}
