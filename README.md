# Лабораторная работа № 3 — Docker и Kubernetes

Учебный проект по дисциплине Distributed Systems: контейнеризация Flask REST API, запуск через Docker Compose и развёртывание нескольких реплик в Kubernetes.

## Цель и реализация

Приложение не хранит состояние и слушает порт 5000. Эндпоинт `GET /time` возвращает поля `time` и `served_by` (hostname контейнера или pod). По `served_by` можно наблюдать распределение запросов. Эндпоинт `POST /echo` возвращает переданное поле `message`; отсутствие поля даёт HTTP 400.

| Файл | Назначение |
|---|---|
| `app/app.py` | REST API v2 |
| `app/requirements.txt` | Зависимости Python |
| `app/Dockerfile` | Образ на базе Python 3.12 slim |
| `docker-compose.yml` | Запуск API с публикацией порта 5000 |
| `k8s/deployment.yaml` | Deployment `my-api`, 3 реплики |
| `k8s/service.yaml` | NodePort Service: порт 80 → 5000 |
| [spec.md](spec.md) | Спецификация |
| [Lab3_Reflection_Report.pdf](Lab3_Reflection_Report.pdf) | Отчёт |
| [screenshots/](screenshots/) | Скриншоты экспериментов |

Файлы `broker.py`, `producer.py`, `consumer.py` сохранены из Lab 2 для справки и не входят в контейнер или Kubernetes-развёртывание Lab 3.

## Запуск через Docker Compose

Требуются работающий Docker Engine и Docker Compose v2. Из корня проекта:

```bash
docker compose up --build -d
docker compose ps
```

Откройте http://localhost:5000/time. Для остановки:

```bash
docker compose down
```

## Запуск в Kubernetes (Minikube)

Требуются Docker, kubectl и Minikube.

```bash
minikube start
docker build -t my-api:lab3 ./app
minikube image load my-api:lab3
kubectl apply -f k8s/
kubectl rollout status deployment/my-api
kubectl get pods -l app=my-api
minikube service my-api --url
```

Используйте выведенный адрес Service, добавив `/time`. Если Minikube держит туннель в текущем терминале, оставьте его открытым и выполняйте запросы из другого.

## Эксперименты

1. Отправьте 30 отдельных запросов `GET /time` через Service и сравните `served_by`: ожидаются как минимум два разных pod; равномерное распределение не гарантируется.
2. Получите имена pod командой `kubectl get pods -l app=my-api`, затем выполните `kubectl delete pod <имя-pod>`. Наблюдайте восстановление числа реплик командой `kubectl get pods -l app=my-api -w`.
3. Увеличьте число реплик до пяти, затем верните три:

```bash
kubectl scale deployment my-api --replicas=5
kubectl rollout status deployment/my-api
kubectl get pods -l app=my-api
kubectl scale deployment my-api --replicas=3
kubectl rollout status deployment/my-api
```

4. Проверьте `POST /echo` с JSON `{"message":"Hello"}` (200) и без поля `message` (400).

Скриншоты и PDF находятся по ссылкам выше. Наличие манифестов само по себе не подтверждает успешное выполнение экспериментов.

## Очистка

```bash
kubectl delete -f k8s/
minikube stop
```

## История ветки

Ветка `lab3` создана на исходном коммите `0a80875` (`lab3`) с сохранением его предшествующей истории. README и перенос PDF-отчёта в корень добавлены отдельным коммитом.
