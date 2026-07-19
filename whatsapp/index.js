const qrcode = require("qrcode-terminal");
const axios = require("axios");

const {
    default: makeWASocket,
    useMultiFileAuthState
} = require("@whiskeysockets/baileys");

const pino = require("pino");


const API_URL = "http://127.0.0.1:5000/chat";



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




async function iniciarBot() {


    const { state, saveCreds } =
        await useMultiFileAuthState("auth");



    const sock = makeWASocket({

        auth: state,

        logger: pino({
            level: "silent"
        })

    });



    sock.ev.on(
        "creds.update",
        saveCreds
    );




    sock.ev.on(
        "connection.update",
        ({ connection, qr }) => {



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

                console.log(
                    "\n✅ WhatsApp conectado!\n"
                );

            }




            if (connection === "close") {


                console.log(
                    "\n❌ WhatsApp desconectado."
                );


                console.log(
                    "🔄 Tentando reconectar em 5 segundos...\n"
                );



                setTimeout(() => {

                    iniciarBot();

                }, 5000);


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



iniciarBot();