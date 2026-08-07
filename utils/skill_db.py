"""
utils/skill_db.py
Curated skill keyword database grouped by category.
Used as fallback when spaCy/SkillNer is unavailable.
"""

# ─────────────────────────────────────────
# PROGRAMMING LANGUAGES
# ─────────────────────────────────────────
LANGUAGES = [
    "Python", "Java", "JavaScript", "TypeScript", "C", "C++", "C#", "Go",
    "Rust", "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB",
    "Perl", "Haskell", "Erlang", "Elixir", "Dart", "Lua", "Shell", "Bash",
    "PowerShell", "SQL", "PL/SQL", "T-SQL", "GraphQL", "COBOL", "Fortran",
    "Assembly", "Julia", "Groovy", "Visual Basic", "VBA",
]

# ─────────────────────────────────────────
# WEB FRAMEWORKS & LIBRARIES
# ─────────────────────────────────────────
WEB_FRAMEWORKS = [
    "React", "Angular", "Vue.js", "Next.js", "Nuxt.js", "Svelte", "Gatsby",
    "Django", "Flask", "FastAPI", "Spring Boot", "Express.js", "NestJS",
    "Laravel", "Rails", "ASP.NET", "Blazor", "Remix", "Astro",
    "jQuery", "Bootstrap", "Tailwind CSS", "Material UI", "Ant Design",
    "Redux", "Zustand", "MobX", "GraphQL Apollo", "REST API", "gRPC",
    "WebSockets", "Node.js", "Deno", "Bun",
]

# ─────────────────────────────────────────
# DATA SCIENCE & ML
# ─────────────────────────────────────────
DATA_ML = [
    "Machine Learning", "Deep Learning", "Neural Networks", "NLP",
    "Natural Language Processing", "Computer Vision", "Reinforcement Learning",
    "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "XGBoost", "LightGBM",
    "CatBoost", "OpenCV", "Hugging Face", "Transformers", "BERT", "GPT",
    "LLM", "Large Language Models", "Stable Diffusion", "Pandas", "NumPy",
    "SciPy", "Matplotlib", "Seaborn", "Plotly", "Tableau", "Power BI",
    "Data Analysis", "Data Science", "Data Engineering", "Data Visualization",
    "Feature Engineering", "Model Training", "Hyperparameter Tuning",
    "A/B Testing", "Statistical Analysis", "Regression", "Classification",
    "Clustering", "Time Series", "Anomaly Detection", "Recommender Systems",
    "spaCy", "NLTK", "MLflow", "Weights & Biases", "DVC",
]

# ─────────────────────────────────────────
# DATABASES
# ─────────────────────────────────────────
DATABASES = [
    "MySQL", "PostgreSQL", "SQLite", "Oracle", "SQL Server", "MariaDB",
    "MongoDB", "Redis", "Cassandra", "DynamoDB", "Elasticsearch", "Neo4j",
    "CouchDB", "InfluxDB", "Firestore", "BigQuery", "Snowflake", "Redshift",
    "Databricks", "Apache Hive", "HBase", "Teradata", "Supabase", "PlanetScale",
    "Pinecone", "Weaviate", "ChromaDB", "Milvus",
]

# ─────────────────────────────────────────
# CLOUD PLATFORMS & DEVOPS
# ─────────────────────────────────────────
CLOUD_DEVOPS = [
    "AWS", "Azure", "GCP", "Google Cloud", "IBM Cloud", "Heroku", "DigitalOcean",
    "Vercel", "Netlify", "Cloudflare", "Docker", "Kubernetes", "Terraform",
    "Ansible", "Chef", "Puppet", "Jenkins", "GitHub Actions", "GitLab CI",
    "CircleCI", "Travis CI", "ArgoCD", "Helm", "Prometheus", "Grafana",
    "Datadog", "Splunk", "ELK Stack", "Kafka", "RabbitMQ", "Celery",
    "CI/CD", "DevOps", "MLOps", "Site Reliability Engineering", "SRE",
    "Infrastructure as Code", "IaC", "Microservices", "Serverless",
    "Lambda", "EC2", "S3", "ECS", "EKS", "GKE", "AKS",
]

# ─────────────────────────────────────────
# TOOLS & PRACTICES
# ─────────────────────────────────────────
TOOLS = [
    "Git", "GitHub", "GitLab", "Bitbucket", "Jira", "Confluence", "Notion",
    "Slack", "Figma", "Adobe XD", "Sketch", "Postman", "Swagger", "OpenAPI",
    "VS Code", "IntelliJ", "PyCharm", "Eclipse", "Xcode", "Android Studio",
    "Linux", "Unix", "Windows Server", "macOS", "Nginx", "Apache",
    "Webpack", "Vite", "Babel", "ESLint", "Prettier", "Jest", "Pytest",
    "Selenium", "Cypress", "Playwright", "Mocha", "JUnit",
    "Agile", "Scrum", "Kanban", "Waterfall", "TDD", "BDD",
]

# ─────────────────────────────────────────
# SECURITY
# ─────────────────────────────────────────
SECURITY = [
    "Cybersecurity", "Penetration Testing", "Ethical Hacking", "OWASP",
    "OAuth", "JWT", "SSL/TLS", "Encryption", "PKI", "Zero Trust",
    "SIEM", "SOC", "Vulnerability Assessment", "Incident Response",
    "Firewalls", "VPN", "IAM", "GDPR", "HIPAA", "SOC 2", "ISO 27001",
]

# ─────────────────────────────────────────
# SOFT SKILLS
# ─────────────────────────────────────────
SOFT_SKILLS = [
    "Leadership", "Communication", "Teamwork", "Problem Solving",
    "Critical Thinking", "Creativity", "Adaptability", "Time Management",
    "Project Management", "Stakeholder Management", "Mentoring",
    "Cross-functional Collaboration", "Presentation Skills",
    "Technical Writing", "Documentation", "Customer Focus",
    "Analytical Thinking", "Decision Making",
]

# ─────────────────────────────────────────
# DOMAIN-SPECIFIC
# ─────────────────────────────────────────
DOMAIN = [
    "Blockchain", "Smart Contracts", "Solidity", "Web3", "IoT",
    "Embedded Systems", "FPGA", "RTOS", "Robotics", "ROS",
    "Augmented Reality", "Virtual Reality", "AR/VR", "Game Development",
    "Unity", "Unreal Engine", "Mobile Development", "React Native",
    "Flutter", "iOS", "Android", "SAP", "ERP", "CRM", "Salesforce",
    "Product Management", "Business Analysis", "Digital Marketing",
    "SEO", "SEM", "Google Analytics", "Data Warehousing", "ETL",
    "Business Intelligence", "Finance", "Quantitative Analysis",
]

# ─────────────────────────────────────────
# Combined master skill list
# ─────────────────────────────────────────
ALL_SKILLS: list[str] = (
    LANGUAGES
    + WEB_FRAMEWORKS
    + DATA_ML
    + DATABASES
    + CLOUD_DEVOPS
    + TOOLS
    + SECURITY
    + SOFT_SKILLS
    + DOMAIN
)

# Lowercase lookup set for fast membership testing
ALL_SKILLS_LOWER: set[str] = {s.lower() for s in ALL_SKILLS}

# Category map for skill → category lookup
SKILL_CATEGORIES: dict[str, str] = {}
for _cat, _skills in [
    ("Programming Language", LANGUAGES),
    ("Web Framework", WEB_FRAMEWORKS),
    ("Data / ML", DATA_ML),
    ("Database", DATABASES),
    ("Cloud / DevOps", CLOUD_DEVOPS),
    ("Tool / Practice", TOOLS),
    ("Security", SECURITY),
    ("Soft Skill", SOFT_SKILLS),
    ("Domain", DOMAIN),
]:
    for _skill in _skills:
        SKILL_CATEGORIES[_skill.lower()] = _cat
