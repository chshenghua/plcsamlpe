#include <windows.h>
#include <stdio.h>
#include <math.h>
#include <CommCtrl.h>
#pragma comment(lib, "comctl32.lib")
#pragma comment(linker,"\"/manifestdependency:type='win32' \
name='Microsoft.Windows.Common-Controls' version='6.0.0.0' \
processorArchitecture='*' publicKeyToken='6595b64144ccf1df' language='*'\"")

// K���ȵ�ż�¶�-�ȵ��ƶ��ձ���չ���ݣ�
struct ThermocouplePair {
    int temp;       // �¶ȣ���C��
    double emf;     // �ȵ��ƣ�mV��
};

const struct ThermocouplePair k_type_table[] = {
    {0, 0.000},
    {50, 2.023},
    {100, 4.096},
    {150, 6.138},
    {200, 8.138},
    {250, 10.153},
    {300, 12.209},
    {350, 14.293},
    {400, 16.397},
    {450, 18.516},
    {500, 20.644},
    {550, 22.776},
    {600, 24.905},
    {650, 27.025},
    {700, 29.129},
    {750, 31.213},
    {800, 33.275},
    {850, 35.313},
    {900, 37.326},
    {950, 39.314},
    {1000, 41.276}
};

#define ID_EDIT 1
#define ID_BUTTON 2
#define ID_RESULT 3

HWND hEdit, hButton, hResult;
int g_table_size;

// ���Բ�ֵ����
double interpolate(double temp) {
    for (int i = 0; i < g_table_size - 1; i++) {
        if (temp >= k_type_table[i].temp && temp <= k_type_table[i + 1].temp) {
            double t1 = k_type_table[i].temp;
            double t2 = k_type_table[i + 1].temp;
            double e1 = k_type_table[i].emf;
            double e2 = k_type_table[i + 1].emf;
            return e1 + (temp - t1) * (e2 - e1) / (t2 - t1);
        }
    }
    return -1;
}

// �����ؼ�
void CreateControls(HWND hwnd) {
    CreateWindow("STATIC", "�����¶�(��C):", 
        WS_CHILD | WS_VISIBLE,
        10, 20, 90, 20, hwnd, NULL, 
        GetModuleHandle(NULL), NULL);

    hEdit = CreateWindow("EDIT", "",
        WS_CHILD | WS_VISIBLE | WS_BORDER | ES_AUTOHSCROLL,
        100, 20, 180, 25, hwnd, (HMENU)ID_EDIT,
        GetModuleHandle(NULL), NULL);

    hButton = CreateWindow("BUTTON", "��ѯ",
        WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
        290, 20, 80, 25, hwnd, (HMENU)ID_BUTTON,
        GetModuleHandle(NULL), NULL);

    hResult = CreateWindow("STATIC", "�������¶ȣ�0-1000��C��",
        WS_CHILD | WS_VISIBLE | SS_CENTER,
        10, 60, 360, 80, hwnd, (HMENU)ID_RESULT,
        GetModuleHandle(NULL), NULL);

    // ����Ĭ�Ͻ���
    SetFocus(hEdit);
}

// ���ڹ���
LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam) {
    switch (uMsg) {
        case WM_CREATE:
            CreateControls(hwnd);
            return 0;

        case WM_COMMAND:
            if (LOWORD(wParam) == ID_BUTTON) {
                char buffer[256] = {0};
                GetWindowText(hEdit, buffer, sizeof(buffer));
                
                if (strlen(buffer) == 0) {
                    SetWindowText(hResult, "�������¶�ֵ��");
                    return 0;
                }

                double temp = atof(buffer);
                if (temp < 0 || temp > 1000) {
                    SetWindowText(hResult, "�¶ȳ�����Χ��������0-1000��C֮����¶ȡ�");
                } else {
                    double emf = interpolate(temp);
                    if (emf >= 0) {
                        char result[256];
                        sprintf(result, "�¶ȣ�%.1f��C\r\n�ȵ��ƣ�%.3f mV", temp, emf);
                        SetWindowText(hResult, result);
                    } else {
                        SetWindowText(hResult, "�������");
                    }
                }
            }
            return 0;

        case WM_DESTROY:
            PostQuitMessage(0);
            return 0;
    }
    return DefWindowProc(hwnd, uMsg, wParam, lParam);
}

// �������
int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, 
    LPSTR lpCmdLine, int nCmdShow) {
    
    g_table_size = sizeof(k_type_table) / sizeof(k_type_table[0]);

    // ע�ᴰ����
    const char CLASS_NAME[] = "K���ȵ�ż��ѯ����";
    WNDCLASS wc = {0};
    wc.lpfnWndProc = WindowProc;
    wc.hInstance = hInstance;
    wc.lpszClassName = CLASS_NAME;
    wc.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    
    if (!RegisterClass(&wc)) {
        MessageBox(NULL, "����ע��ʧ�ܣ�", "����", MB_OK | MB_ICONERROR);
        return 0;
    }

    // ����������
    HWND hwnd = CreateWindow(CLASS_NAME,
        "K���ȵ�ż�¶�-�ȵ��Ʋ�ѯ����",
        WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX,
        CW_USEDEFAULT, CW_USEDEFAULT, 400, 200,
        NULL, NULL, hInstance, NULL);

    if (!hwnd) {
        MessageBox(NULL, "���ڴ���ʧ�ܣ�", "����", MB_OK | MB_ICONERROR);
        return 0;
    }

    ShowWindow(hwnd, nCmdShow);
    UpdateWindow(hwnd);

    // ��Ϣѭ��
    MSG msg = {0};
    while (GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }

    return msg.wParam;
}