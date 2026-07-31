const qrcode = require("qrcode-terminal");
const axios = require("axios");
const fs = require("fs");
const path = require("path");

const {
    default: makeWASocket,
    useMultiFileAuthState,
    DisconnectReason,
    fetchLatestBaileysVersion
} = require("@whiskeysockets/baileys");

const pino = require("pino");


const API_URL = "http://127.0.0.1:5000/chat";
const AUTH_DIR = path.resolve(__dirname, "..", "auth");

let socketAtivo = null;
let timerReconexao = null;


async function enviarMensagem(sock, jid, texto) {

    try {

        const resultado = await sock.sendMessage(
            jid,
            {
                text: texto
            }
        );


        console.log(
            "✅ Mensagem enviada:",
            resultado.key.id
        );


        return resultado;


    } catch (erro) {


        console.log(
            "⚠️ Falha no envio. Tentando novamente..."
        );


        await new Promise(
            resolve => setTimeout(resolve, 3000)
        );


        return await sock.sendMessage(
            jid,
            {
                text: texto
            }
        );

    }

}


function obterCodigoErro(erro) {

    return (
        erro?.output?.statusCode ||
        erro?.data?.statusCode ||
        erro?.statusCode ||
        erro?.status
    );

}


function limparAuth() {

    if (fs.existsSync(AUTH_DIR)) {
        fs.rmSync(AUTH_DIR, { recursive: true, force: true });
    }

    fs.mkdirSync(AUTH_DIR, { recursive: true });

}


function agendarReconexao(segundos = 5) {

    if (timerReconexao) {
        clearTimeout(timerReconexao);
    }

    console.log(`🔄 Tentando reconectar em ${segundos} segundos...\n`);

    timerReconexao = setTimeout(() => {

        iniciarBot().catch((erro) => {
            console.log("❌ Falha ao reiniciar bot:", erro.message);
        });

    }, segundos * 1000);

}


async function iniciarBot() {


    if (!fs.existsSync(AUTH_DIR)) {
        fs.mkdirSync(AUTH_DIR, { recursive: true });
    }


    const { state, saveCreds } =
        await useMultiFileAuthState(AUTH_DIR);


    const {
        version,
        isLatest
    } = await fetchLatestBaileysVersion();

    console.log(
        `🧩 Versão WA Web usada: ${version.join(".")} (latest: ${isLatest ? "sim" : "não"})`
    );



    const sock = makeWASocket({

        auth: state,

        version,

        printQRInTerminal: false,

        logger: pino({
            level: "error"
        })

    });


    socketAtivo = sock;


    sock.ev.on(
        "creds.update",
        saveCreds
    );




    sock.ev.on(
        "connection.update",
        ({ connection, qr, lastDisconnect }) => {


            if (connection) {
                console.log(`ℹ️ Estado da conexão: ${connection}`);
            }


            if (qr) {

                console.log(
                    "\n📱 Escaneie o QR Code:\n"
                );


                qrcode.generate(
                    qr,
                    {
                        small: true
                    }
                );

            }


            if (connection === "open") {

                if (timerReconexao) {
                    clearTimeout(timerReconexao);
                    timerReconexao = null;
                }

                console.log(
                    "\n✅ WhatsApp conectado!\n"
                );

                console.log(`📁 Sessão sendo persistida em: ${AUTH_DIR}`);

            }


            if (connection === "close") {


                const codigo = obterCodigoErro(lastDisconnect?.error);
                const motivo =
                    lastDisconnect?.error?.message ||
                    "erro não informado";


                console.log(`🧩 Código de desconexão: ${codigo ?? "desconhecido"}`);
                console.log(`🧩 Motivo bruto: ${motivo}`);


                console.log(
                    "\n❌ WhatsApp desconectado."
                );


                if (socketAtivo !== sock) {
                    return;
                }


                if (codigo === DisconnectReason.loggedOut) {

                    console.log(
                        "🧹 Sessão inválida. Limpando auth para gerar novo QR..."
                    );

                    limparAuth();
                    agendarReconexao(2);
                    return;
                }


                if (codigo === DisconnectReason.restartRequired) {

                    console.log(
                        "♻️ Reinício solicitado pelo WhatsApp. Recriando conexão..."
                    );

                    agendarReconexao(1);
                    return;
                }


                console.log(
                    "⚠️ Desconexão transitória detectada."
                );

                agendarReconexao(5);


            }


        }
    );





    sock.ev.on(
        "messages.upsert",
        async ({ messages }) => {



            const msg = messages[0];



            if (!msg.message)
                return;



            if (msg.key.fromMe)
                return;




            const texto =
                msg.message.conversation ||
                msg.message.extendedTextMessage?.text ||
                "";




            if (!texto.trim())
                return;




            const destinatario =
                msg.key.remoteJidAlt ||
                msg.key.remoteJid;



            const numero =
                destinatario.split("@")[0];




            console.log("\n====================");

            console.log(
                "📩 Mensagem:",
                texto
            );


            console.log(
                "👤 Número:",
                numero
            );





            try {



                console.log(
                    "🧠 Enviando para IA..."
                );




                const resposta =
                    await axios.post(

                        API_URL,

                        {
                            numero: numero,
                            mensagem: texto
                        },

                        {
                            timeout: 120000
                        }

                    );




                const respostaIA =
                    resposta.data.resposta;





                console.log(
                    "🤖 IA:",
                    respostaIA
                );





                await enviarMensagem(
                    sock,
                    destinatario,
                    respostaIA
                );





            } catch (erro) {



                console.log(
                    "❌ Erro:",
                    erro.message
                );





                await enviarMensagem(

                    sock,

                    destinatario,

                    "Estou com dificuldade para responder agora 🤖"

                );


            }




            console.log(
                "====================\n"
            );



        }
    );



}



iniciarBot().catch((erro) => {
    console.log("❌ Erro fatal ao iniciar bot:", erro.message);
});
