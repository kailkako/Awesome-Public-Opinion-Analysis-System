import pandas as pd
import folium
from folium.plugins import HeatMap

# 读取新的 CSV 文件（article.csv）
df = pd.read_csv('article.csv')

# 重命名列名为统一格式（可选）
df.rename(columns={
    'likeNum': 'like_num',
    'commentsLen': 'comment_num',
    'reposts_count': 'forward_num',
    'region': 'location_name'
}, inplace=True)

# 清除缺失位置数据
df = df.dropna(subset=['location_name'])

# 按地区计算平均互动指标
location_stats = df.groupby('location_name')[['forward_num', 'comment_num', 'like_num']].mean().reset_index()

# 中国省份经纬度映射
location_coords = {
    '北京': [39.9042, 116.4074],
    '天津': [39.3434, 117.3616],
    '上海': [31.2304, 121.4737],
    '重庆': [29.4316, 106.9123],
    '河北': [38.0428, 114.5149],
    '山西': [37.8735, 112.5624],
    '辽宁': [41.8354, 123.4291],
    '吉林': [43.8965, 125.3259],
    '黑龙江': [45.7421, 126.6617],
    '江苏': [32.9711, 119.0264],
    '浙江': [29.1163, 119.1994],
    '安徽': [31.8612, 117.2857],
    '福建': [26.0753, 119.3062],
    '江西': [27.6140, 115.7221],
    '山东': [36.6758, 117.0009],
    '河南': [34.7655, 113.7533],
    '湖北': [30.9845, 112.2707],
    '湖南': [27.6104, 111.7080],
    '广东': [23.3790, 113.7633],
    '海南': [19.5664, 109.9497],
    '四川': [30.6516, 104.0759],
    '贵州': [26.5982, 106.7074],
    '云南': [24.8801, 102.8329],
    '陕西': [34.2655, 108.9542],
    '甘肃': [36.0594, 103.8263],
    '青海': [36.6232, 101.7782],
    '台湾': [23.6978, 120.9605],
    '内蒙古': [40.8183, 111.7652],
    '广西': [23.7248, 108.3200],
    '西藏': [31.6846, 88.0924],
    '宁夏': [37.1987, 106.1581],
    '新疆': [43.7928, 87.6177],
    '香港': [22.3193, 114.1694],
    '澳门': [22.1987, 113.5439],
}

# 匹配坐标
location_stats['coords'] = location_stats['location_name'].map(location_coords)

# 移除没有坐标的地区
location_stats = location_stats.dropna(subset=['coords'])

# 创建地图
m = folium.Map(location=[35.8617, 104.1954], zoom_start=5)

# 添加热力图层
heat_maps = []
for metric, name in zip(['forward_num', 'comment_num', 'like_num'], ['转发量', '评论量', '点赞量']):
    heat_data = [[row['coords'][0], row['coords'][1], row[metric]] for index, row in location_stats.iterrows()]
    heat_map = HeatMap(heat_data, name=name)
    heat_maps.append(heat_map)
    heat_map.add_to(m)

# 添加图层控制器
folium.LayerControl().add_to(m)

# 保存结果
m.save('文章互动热力图.html')
