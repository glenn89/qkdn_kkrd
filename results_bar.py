# import numpy as np
# import matplotlib.pyplot as plt
#
# # 데이터 생성
# categories = ['Random', 'Centrality', 'Distance+Centrality']
# values1 = [277, 255, 239]
# values2 = [49.22, 44.32, 54.06]
#
# x = np.arange(len(categories))  # X축 위치
# bar_width = 0.4  # 막대 너비
#
# # 첫 번째 축 생성 (왼쪽 Y축)
# fig, ax1 = plt.subplots(figsize=(8, 5))
#
# ax1.bar(x - bar_width/2, values1, width=bar_width, label='Dataset 1', color='skyblue')
# ax1.set_ylabel('The number of session block', color='blue')
# # ax1.set_xlabel('Categories')
# ax1.set_xticks(x)
# ax1.set_xticklabels(categories)
# ax1.tick_params(axis='y', labelcolor='blue')
# ax1.set_ylim(200, 300)
#
# # 두 번째 축 생성 (오른쪽 Y축)
# ax2 = ax1.twinx()  # 오른쪽 Y축 추가
# ax2.bar(x + bar_width/2, values2, width=bar_width, label='Dataset 2', color='salmon')
# ax2.set_ylabel('Key usage ratio', color='red')
# ax2.tick_params(axis='y', labelcolor='red')
# ax2.set_ylim(40, 60)
#
#
# # # 범례 추가
# # ax1.legend(loc='upper left')
# # ax2.legend(loc='upper right')
#
# # 그래프 출력
# plt.title('Lifetime-aware key relay')
# plt.show()

import numpy as np
import matplotlib.pyplot as plt

# 데이터 생성
# categories = ['Simple SP', 'Weighted SP', 'Lifetime-aware SP']
categories = ['Shortest path \n key relay', 'Weighted shortest \n path key relay', 'Lifetime-aware \n key relay']
values3 = [778, 782, 794]  # 세 번째 데이터
values2 = [588, 599, 587]
# values1 = np.arange(0, 10, 1)

# values3 = [774.18, 811.8, 928.08]  # 세 번째 데이터
# values2 = [253.96, 274.64, 274.82]
# values1 = [53.86, 64.11]

x = np.arange(len(categories))  # X축 위치
bar_width = 0.3  # 막대 너비
bar_spacing = 0.25

# 그래프 생성
fig, ax = plt.subplots(figsize=(18, 20))
colors = ['#2F4554', '#2F4554', '#2F4554']

# 막대 그래프 추가
ax.bar(x - bar_width / 2, values3, width=bar_width, label='Non-proactive key relay', color='white', edgecolor='black', hatch='/')
ax.bar(x + bar_width / 2, values2, width=bar_width, label='Proactive key relay', color=colors, edgecolor='black')
# ax.plot(x, values1, label='Distance+Centrality', linewidth=2, marker='o')

# X축 설정
ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=30) # , rotation=45

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
