
import numpy as np
import matplotlib.pyplot as plt

# 데이터 생성
# categories = ['Simple SP', 'Weighted SP', 'Lifetime-aware SP']
categories = ['Shortest path \n key relay', 'Weighted shortest \n path key relay', 'Lifetime-aware \n key relay']
values3 = [230, 236,	254,	269,	288,	382,	396,	399,	399,	399,	399,	399,	399,	399]  # 세 번째 데이터
values2 = [226,	235,	252,	267,	286,	383,	402,	403,	403,	403,	403,	403,	403,	403]
values1 = [226,	232,	252,	271,	288,	384,	397,	401,	401,	401,	401,	401,	401,	401]

# values3 = [72.5,	73.24,	73.22,	73.06,	72.1,	70.86,	69.98,	70.48,	70.48,	70.48,	70.48,	70.48,	70.48,	70.48]  # 세 번째 데이터
# values2 = [72.26,	72.92,	73.72,	73.54,	73.96,	72.32,	72.92,	73.14,	73.14,	73.14,	73.14,	73.14,	73.14,	73.14]
# values1 = [72.08,	72.26,	73.84,	76.22,	74.12,	75.72,	74.98,	76.28,	76.28,	76.28,	76.28,	76.28,	76.28,	76.28]

x = np.arange(1, 15, 1)  # X축 위치

# 그래프 생성
fig, ax = plt.subplots(figsize=(25, 15))
colors = ['#2F4554', '#2F4554', '#2F4554']
ax.plot(x, values3, label='shortest path key relay', linewidth=2, marker='o')
ax.plot(x, values2, label='weighed shortest path key relay', linewidth=2, marker='o')
ax.plot(x, values1, label='liftime-aware key relay', linewidth=2, marker='o')

# X축 설정
ax.set_xticks(x)
ax.set_xticklabels(x, fontsize=30) # , rotation=45
ax.set_xlabel('Threshold', fontsize=30)

# Y축 설정 (오른쪽 Y축 제거)
ax.set_ylabel('The number of service provision', fontsize=30)
# ax.set_ylabel('Average delay', fontsize=30)
# ax.yaxis.set_label_position("left")  # Y축을 왼쪽으로 설정 (기본값)
# ax.yaxis.tick_left()  # 왼쪽 Y축만 사용
ax.tick_params(axis='y', labelsize=30, direction='in', length=30)
# ax.set_yticks([200, 400, 600, 800, 1000])
# ax.set_yticks([10, 30, 50, 70])

# 그래프 제목 및 범례 추가
plt.legend(loc='best', framealpha=0.9, fontsize=30)

# 그래프 출력
plt.show()
