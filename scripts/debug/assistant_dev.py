from openai import OpenAI
import os, sys, yaml

# === 🧠 LOAD AGENT PROFILE ===
agent_path = "agents/claude-dev.yaml"
with open(agent_path, "r") as f:
    agent = yaml.safe_load(f)

# === 🔐 API CLIENT ===
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === 💬 USER PROMPT ===
if len(sys.argv) < 2:
    print("Uso: python assistant_dev.py \"<tu instrucción aquí>\"")
    sys.exit(1)

user_input = sys.argv[1]

system_prompt = f"""
Eres un agente de desarrollo técnico llamado {agent['name']} ({agent['role']}).
Tu versión es {agent['version']}.
Sigue el protocolo Smart Dev System en todas tus respuestas:
1. Analiza antes de modificar.
2. Propón comandos Bash si se requiere auditoría.
3. Espera confirmación antes de ejecutar cambios.
4. No inventes resultados ni supongas configuraciones.
"""

# === 🚀 EXECUTE COMPLETION ===
response = client.chat.completions.create(
    model="gpt-5",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]
)

print("\n=== 🤖 RESPUESTA DEL ASISTENTE ===\n")
print(response.choices[0].message.content)
