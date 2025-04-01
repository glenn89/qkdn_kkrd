
import numpy as np
import matplotlib.pyplot as plt

# 데이터 생성
# categories = ['Simple SP', 'Weighted SP', 'Lifetime-aware SP']
categories = ['Shortest path \n key relay', 'Weighted shortest \n path key relay', 'Lifetime-aware \n key relay']
# values3 = [252, 271, 311, 360, 415,	551, 577, 578, 588,	599, 599, 599]  # 세 번째 데이터
# values2 = [245,	270, 313, 364, 425, 558, 590, 591, 599, 600, 600, 600]
# values1 = [247, 270, 308, 362, 420,	551, 582, 582, 587,	598, 598, 598]

values3 = [213.74, 203.06, 199.96, 200.02, 204.94,	237.04,	248.8,	246.18,	251.72,	251.72,	251.72,	251.72]  # 세 번째 데이터
values2 = [236.5, 229.4, 239.16, 239.26, 252.54, 279.02, 288.82, 284.06, 284.22, 285.3,	285.3, 285.3]
values1 = [213.26,	214.96,	218.54,	218.52,	244.68,	253.48,	275.4,	280.7,	283.5,	285.04,	285.04,	285.04]

x = np.arange(1, 13, 1)  # X축 위치

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
# ax.set_ylabel('The number of service provision', fontsize=30)
ax.set_ylabel('Average delay', fontsize=30)
# ax.yaxis.set_label_position("left")  # Y축을 왼쪽으로 설정 (기본값)
# ax.yaxis.tick_left()  # 왼쪽 Y축만 사용
ax.tick_params(axis='y', labelsize=30, direction='in', length=30)
# ax.set_yticks([200, 400, 600, 800, 1000])
# ax.set_yticks([10, 30, 50, 70])

# 그래프 제목 및 범례 추가
plt.legend(loc='best', framealpha=0.9, fontsize=30)

# 그래프 출력
plt.show()
