#include <windows.h>
#include<stdio.h>
#include<stdlib.h>
#include<complex.h>
#include<math.h>
#define N 64

_Complex float fun(_Complex float x)
{
	return (cpow(x,3) / 2 - 3 * x / 2);
}

_Complex float dfun(_Complex float x)//the diffenential of fun(w)
{
	return (3 * cpow(x,2) / 2 - 3 / 2);
}

float pi = acos(-1);
float aa[4] = {3.1540987,-3.80204639,2.06700525,-0.42654784};
float bb[5] = {0.00046814,0.00187257,0.00280886,0.00187257,0.00046814};
int main()
{
	int count=0,count1=0;
	int sample[195]={0};
	float samplef[195]={0};
	_Complex float Xr[195] = {0};
	_Complex float V3=0,V24=0,V135=0;
	_Complex float w[195]={0},w0=1,w1=0;
	float f[195]={0},df[195]={0};
	_Complex float a[195]={0};
	_Complex float Ar[195]={0};
	float X[195]={0};
	float ff[195]={0};
	float XX[195]={0};
	int flag=0;
	char state='0';
	float f_data[1000]={0};
	float X_data[1000]={0};
	int point_num=0;

	start : while (state == '0')
	{
		if (point_num == 0)
		{
			printf("data�ƶq:");
			scanf("%d",&point_num);
		}
		if (count >= 259)
		{
			count %= 195;
			flag = 1;
		}

		/*中文*/
		scanf("%d",&sample[count % 195]);

		/*butterworth中文*/
		if (count > 3)
			samplef[count % 195] = aa[0]*samplef[(count - 1) % 195] + aa[1]*samplef[(count - 2) % 195] + aa[2]*samplef[(count - 3) % 195] + aa[3]*samplef[(count - 4) % 195]\
						   		  +bb[0]*sample[count % 195] + bb[1]*sample[(count - 1) % 195] + bb[2]*sample[(count - 2) % 195] + bb[3]*sample[(count - 3) % 195] + bb[4]*sample[(count - 4) % 195];

		/*DFT�p��*/
		if (count >= 64 && count < 128 && flag == 0)
			Xr[127] += samplef[count] * cexp(-I * 2.f * pi * (count - 64) / 64.f) * 2 / 64.f;

		/*DFT���N�B��*/
		if (count >= 128 || flag == 1)
			Xr[count % 195] = cexp(I * 2 * pi / 64.f) * \
				(Xr[(count - 1) % 195] - 2 / 64.f * (float)((samplef[(count - 64) % 195] - samplef[(count) % 195])));

		/*w�p��*/
		if (count >= 131 || flag == 1)
		{
			w0 = cos(59.5 / 3840 * 2 * pi) + cos(60.5 / 3840 * 2 * pi);
			V3 = Xr[(count - 2) % 195];
			V24 = Xr[(count - 3) % 195] + Xr[(count - 1) % 195];
			V135 = Xr[(count - 4) % 195] + 2 * Xr[(count - 2) % 195] + Xr[count % 195];
			for(int i = 0;i < 100;i++)
			{
				w1 = w0 - (w0 * fun(w0) * V3 - (w0 + fun(w0)) * V24 + V135) / \
					(fun(w0) * V3 + w0 * dfun(w0) * V3 - (1 + dfun(w0)) * V24);
				if(cabs(creal(w0 - w1)) < pow(10,-6) && cabs(cimag(w0 - w1)) < pow(10,-6))
				{
					w[count % 195] = w1;
					break;
				}
				w0 = w1;
			}
		}

		/*�W�v����*/
		if (count >= 131 || flag == 1)
		{
			f[count % 195] = acos(creal(w[count % 195] / 2)) * 60 * 64.f / 2 / pi;
			df[count % 195] = cabs(f[count % 195] - 60);
		}

		/*a�p��*/
		if (count >= 131 || flag == 1)
		{
			a[count % 195] = cexp(I * acos(creal(w[count % 195] / 2)));
		}

		/*Ar�p��*/
		if (count >= 131 || flag == 1)
		{
			Ar[count % 195] = (-cpow(a[count % 195],3) * Xr[(count - 4) % 195] + (cpow(a[count % 195],6) + cpow(a[count % 195],4) + 1) * Xr[(count - 3) % 195] \
				- (a[count % 195] + cpow(a[count % 195],3) + cpow(a[count % 195],7)) * Xr[(count - 2) % 195] + cpow(a[count % 195],4) * Xr[(count - 1) % 195]) \
				/ (a[count % 195] - 2 * cpow(a[count % 195],3) + 2 * cpow(a[count % 195],7) - cpow(a[count % 195],9));
		}

		/*���T�p��*/
		if (count >= 131 || flag == 1)
		{
			X[count % 195] = cabs(Ar[count % 195]) * 64.f * sin(pi * df[count % 195] / 60 / 64.f) / \
							 sin(pi * df[count % 195] / 60);
		}

		/*�W�v����������*/
		if (count >= 131 && count < 195 && flag == 0)
			ff[194] += f[count] / 64.f;

		/*�W�v���������ȭ��N�B��*/
		if (count > 194 || flag == 1)
		{
			ff[count % 195] = ff[(count - 1) % 195] - (f[(count - 64) % 195] - f[count % 195]) / 64.f;
			f_data[count1 - 195] = ff[count % 195];
		}

		/*���T����������*/
		if (count >= 131 && count < 195 && flag == 0)
			XX[194] += X[count] / 64.f;

		/*���T���������ȭ��N�B��*/
		if (count > 194 || flag == 1)
		{
			XX[count % 195] = XX[(count - 1) % 195] - (X[(count - 64) % 195] - X[count % 195]) / 64.f;
			X_data[count1 - 195] = XX[count % 195];
		}

		if ((count >= 194 || flag == 1) && 0)
		{
			printf("  point\t\t" " sample\t\t" " samplef\t" "Xr-real\t\t" "Xr-imag\t\t " "\n");
			for(int k = 0;k < 195;k++)
			{
				printf("%5d\t\t" "%6d\t\t" "%8.2f\t" "%8.2f\t" "%8.2f\t",k,sample[k],samplef[k],creal(Xr[k]),cimag(Xr[k]));
				printf("\n");
			}
			printf("\n");
			printf("  point\t\t" "w/2\t\t"  "   f\t\t" "   df\t\t" " a-real\t\t" " a-imag\t\t" "\n");
			for(int k = 0;k < 195;k++)
			{
				printf("%5d\t\t" "%f\t" "%8.3f\t" "%8.4f\t" "%8.4f\t" "%8.4f\t",k,creal(w[k]) / 2,f[k],df[k],creal(a[k]),cimag(a[k]));
				printf("\n");
			}
			printf("\n");
			printf("  point\t\t" " Ar-abs\t\t" "   X\t\t"  "  f-avg \t"  " X-avg " "\n");
			for(int k = 0;k < 195;k++)
			{
				printf("%5d\t\t" "%8.3f\t" "%8.3f\t" "%8.3f\t"  "%8.3f\t",k,cabs(Ar[k]),X[k],ff[k],XX[k]);
				printf("\n");
			}
		}
		if (count1 < point_num - 1)
			system("cls");
		if (count1 == (point_num - 1))
		{
			printf("����U�@�B�ާ@(Y/N)\n");
			getchar();
			scanf("%c",&state);
			system("cls");
		}
		count++;
		count1++;
	}
	while (state != 'N' && state != 'n')
	{
		printf("��ܤU�@�B�ʧ@\n");
		printf("\t" "1:���SDFT�p�⵲�G\n");
		printf("\t" "2:����W�v�ή��T���⵲�G\n");
		printf("\t" "3:���s�����W�v\n");
		getchar();
		scanf("%c",&state);
		system("cls");
		switch (state)
		{
			case '1':
			{
				printf("  point\t\t" " sample\t\t" " samplef\t" "Xr-real\t\t" "Xr-imag\t\t " "\n");
				for(int k = 0;k < 195;k++)
				{
					printf("%5d\t\t" "%6d\t\t" "%8.2f\t" "%8.2f\t" "%8.2f\t",k,sample[k],samplef[k],creal(Xr[k]),cimag(Xr[k]));
					printf("\n");
				}
				printf("\n");
				printf("  point\t\t" "w/2\t\t"  "   f\t\t" "   df\t\t" " a-real\t\t" " a-imag\t\t" "\n");
				for(int k = 0;k < 195;k++)
				{
					printf("%5d\t\t" "%f\t" "%8.3f\t" "%8.4f\t" "%8.4f\t" "%8.4f\t",k,creal(w[k]) / 2,f[k],df[k],creal(a[k]),cimag(a[k]));
					printf("\n");
				}
				printf("\n");
				printf("  point\t\t" " Ar-abs\t\t" "   X\t\t"  "  f-avg \t"  " X-avg " "\n");
				for(int k = 0;k < 195;k++)
				{
					printf("%5d\t\t" "%8.3f\t" "%8.3f\t" "%8.3f\t"  "%8.3f\t",k,cabs(Ar[k]),X[k],ff[k],XX[k]);
					printf("\n");
				}
				break;
			}
			case '2':
			{
				printf("  point\t\t" "  f-avg \t" "  X-avg \n");
				for(int k = 0;f_data[k] != 0 || X_data[k] != 0 ;k++)
				{
					printf("%5d\t\t" "%8.3f\t" "%8.3f\t",k + 1,f_data[k],X_data[k]);
					printf("\n");
				}
				break;
			}
			case '3':
			{
				count = 0;
				count1 = 0;
				flag = 0;
				point_num = 0;
				state = '0';
				for (int k = 0;k < 195;k++)
				{
					sample[k]=0;
					samplef[k]=0;
					Xr[k] = 0;
					V3=0,V24=0,V135=0;
					w[k]=0,w0=1,w1=0;
					f[k]=0,df[k]=0;
					a[k]=0;
					Ar[k]=0;
					X[k]=0;
					ff[k]=0;
					XX[k]=0;
				}
				for (int k = 0;k < 1000;k++)
				{
					f_data[k]=0;
					X_data[k]=0;
				}
				system("cls");
				goto start;
				break;
			}
			default :
			{
				system("cls");
				state = 'N';
			}
		}
	}
	if (state == 'N' || state == 'n')
		system("pause");
	return 0;
}
