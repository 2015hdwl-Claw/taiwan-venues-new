# 構建階段
FROM node:18-alpine AS builder

WORKDIR /app

# 複製 package 文件
COPY package*.json ./

# 安裝依賴
RUN npm ci

# 複製源代碼
COPY . .

# 設置生產環境 API URL
ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# 構建
RUN npm run build

# 生產階段
FROM nginx:alpine

# 複製構建結果
COPY --from=builder /app/dist /usr/share/nginx/html

# 複製 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
