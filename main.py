import streamlit as st
import openai
from PIL import Image
import base64
import io
import json
import matplotlib.pyplot as plt

# Sayfa ayarı (mobil uyum + başlık)
st.set_page_config(page_title="📘 YÖKDİL/YDS AI Eğitmen", layout="centered")

# OpenAI API anahtarı (Streamlit Secrets içinde)
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ----------- Yardımcı Fonksiyonlar -----------
def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def log_stat(topic):
    try:
        with open("istatistik.json", "r") as f:
            data = json.load(f)
    except:
        data = {}
    data[topic] = data.get(topic, 0) + 1
    with open("istatistik.json", "w") as f:
        json.dump(data, f)

def show_stats():
    try:
        with open("istatistik.json", "r") as f:
            data = json.load(f)
    except:
        st.info("Henüz istatistik kaydı yok.")
        return
    fig, ax = plt.subplots()
    ax.bar(data.keys(), data.values(), color="#9900cc")
    ax.set_title("📊 Soru Dağılımı")
    ax.set_ylabel("Çözüm Sayısı")
    st.pyplot(fig, use_container_width=True)

def kelime_ekle(kelime, anlam):
    try:
        with open("kelime_defteri.json", "r") as f:
            defter = json.load(f)
    except:
        defter = {}
    defter[kelime] = anlam
    with open("kelime_defteri.json", "w") as f:
        json.dump(defter, f)

def kelime_defterini_goster():
    try:
        with open("kelime_defteri.json", "r") as f:
            defter = json.load(f)
    except:
        st.info("Henüz kelime eklenmemiş.")
        return
    st.markdown("### 📖 Kelime Defteri")
    for kelime, anlam in defter.items():
        st.markdown(f"🔹 **{kelime}** → _{anlam}_")

# ----------- Sistem Promptu -----------
SYSTEM_PROMPT = """
Sen bir İngilizce sınav eğitmenisin. YÖKDİL ve YDS sınavlarında çıkan sorulara açıklayıcı ve öğretici bir şekilde yanıt veriyorsun.
Sana gönderilen soru görselinde veya yazısında ne sorulduğunu dikkatle analiz et.
Yanıtını aşağıdaki 3 başlık altında ver:

1. ✅ Doğru Cevap: (sadece şık belirt - örn: C)
2. 📘 Açıklama: (sorunun çözüm mantığını açıkla, gramer ya da anlam bilgisi ver)
3. 📊 Sınav Notu: (YÖKDİL/YDS'de bu soru tipi ne kadar yaygın? Konunun sıklığı ve önem derecesini X/10 olarak belirt)

Yanıt sonunda öğrencinin konuyu pekiştirmesi için benzer bir örnek soru üret.
"""
# ----------- Ana Arayüz -----------
st.markdown("<h1 style='text-align:center;'>📘 YÖKDİL / YDS Akıllı Eğitmen</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📝 Soru Çöz", "📊 İstatistik", "📖 Kelime Defteri"])

st.info("📱 Mobil kullanıcılar: Görsel yükleme alanına tıklayarak doğrudan kamera ile fotoğraf çekebilirsiniz.")


# ----------- TAB 1: Soru Çözümü -----------
with tab1:
    st.markdown("💬 Sorunun görselini veya metnini gönder, AI sana açıklamalı şekilde anlatsın!")

    col1, col2 = st.columns(2)
    with col1:
        input_text = st.text_area("✏️ Soru Metni:", placeholder="Metin girmek isteğe bağlı...", height=150)
    with col2:
        uploaded_file = st.file_uploader(
            "📷 Soru Görseli Yükle veya Kamerayla Çek:",
            type=["png", "jpg", "jpeg"],
            help="Mobil cihaz kullanıyorsan bu alana tıklayıp doğrudan kamera ile fotoğraf çekebilirsin."
        )

    if st.button("🔍 Açıklamalı Cevap Al", use_container_width=True):
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        if input_text:
            messages.append({"role": "user", "content": input_text})

        if uploaded_file:
            image = Image.open(uploaded_file)
            base64_img = image_to_base64(image)
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": "Aşağıdaki görseldeki soruyu çöz ve açıkla:"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_img}"}}
                ]
            })

        with st.spinner("AI soruyu analiz ediyor..."):
            response = openai.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=messages,
                max_tokens=1000
            )
            yanit = response.choices[0].message.content
            st.success("✅ Cevap Geldi!")
            st.markdown(yanit)

        topic = st.text_input("📚 Bu sorunun konusu (ör: bağlaç, zaman, kelime bilgisi):")
        if topic:
            log_stat(topic)

        if st.checkbox("➕ Kelime Ekle"):
            kelime = st.text_input("Kelime:")
            anlam = st.text_input("Anlamı:")
            if st.button("📌 Kaydet", use_container_width=True):
                kelime_ekle(kelime, anlam)
                st.success("✅ Kelime eklendi!")

# ----------- TAB 2: İstatistik -----------
with tab2:
    show_stats()

# ----------- TAB 3: Kelime Defteri -----------
with tab3:
    kelime_defterini_goster()
