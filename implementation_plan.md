# שלב 5: ניטור ומעקב (Observability)

המטרה של השלב הזה היא להוסיף יכולות ניטור לאפליקציה, כך שנוכל לראות בזמן אמת כמה משאבים (CPU/RAM) הקונטיינרים לוקחים, מה זמני התגובה של שרת ה-Flask שלנו, ולקבל מסכים גרפיים יפים למעקב.

## User Review Required

> [!IMPORTANT]
> השלב הזה יוסיף כלי ניטור שירוצו על השרת שלך. פורט **3000** ייפתח כדי שתוכל לגשת לממשק של Grafana מכל דפדפן. 
> Grafana יגיע עם ממשק התחברות (שם משתמש וסיסמה ראשוניים שניהם `admin`), ותתבקש לשנות סיסמה בהתחברות הראשונה. האם זה מקובל עליך?

## Proposed Changes

---

### App Metrics (Flask)

#### [MODIFY] [requirements.txt](file:///home/yaakov/Desktop/CashFlow/requirements.txt)
- הוספת הספרייה `prometheus-flask-exporter` כדי לחשוף אוטומטית מטריקות משרת הפייתון שלנו (זמני תגובה, כמות בקשות לכל נתיב, שגיאות HTTP).

#### [MODIFY] [app.py](file:///home/yaakov/Desktop/CashFlow/app.py)
- ייבוא ואתחול של `PrometheusMetrics(app)` כדי שנקודת הקצה `/metrics` תיווצר ותחשוף נתונים ל-Prometheus.

---

### Monitoring Infrastructure

#### [MODIFY] [docker-compose.yml](file:///home/yaakov/Desktop/CashFlow/docker-compose.yml)
הוספת 3 קונטיינרים חדשים למערכת:
1. **cAdvisor**: כלי של גוגל שקורא מטריקות ישירות ממנוע ה-Docker (צריכת מעבד וזיכרון של כל קונטיינר).
2. **Prometheus**: מסד הנתונים שאוסף את כל המטריקות מ-cAdvisor ומ-Flask כל 15 שניות.
3. **Grafana**: מערכת הדשבורדים שתתחבר ל-Prometheus ותציג גרפים ויזואליים.

#### [NEW] [prometheus.yml](file:///home/yaakov/Desktop/CashFlow/prometheus/prometheus.yml)
- יצירת קובץ הגדרות חדש עבור Prometheus, שיורה לו מאיפה לשאוב נתונים (מ-cAdvisor ומ-Flask `app:5000`).

---

### Cloud Infrastructure (Terraform)

#### [MODIFY] [main.tf](file:///home/yaakov/Desktop/CashFlow/terraform/main.tf)
- הוספת חוק (Rule) ל-Security Group של השרת (`aws_security_group.app_sg`) לפתיחת פורט `3000` (הפורט של Grafana) לגישה מבחוץ (`0.0.0.0/0`), בדיוק כמו פורט 80.

## Verification Plan

### Automated Tests
- ה-CI ב-GitHub Actions ימשיך להריץ את הטסטים ויבנה את ה-Docker Image החדש של האפליקציה (שכולל עכשיו את רכיב הניטור).

### Manual Verification
- פריסה אוטומטית ל-EC2 בסיום ה-Pipeline.
- כניסה לכתובת `http://16.171.14.104:3000` כדי לוודא ש-Grafana עובד וזמין לאינטרנט.
- התחברות ל-Grafana, הוספת Prometheus כמקור נתונים (Data Source) ובניית דשבורד ראשון שרואה את ביצועי האפליקציה!
