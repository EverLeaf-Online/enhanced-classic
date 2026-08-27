const readline=require("readline");
const bcrypt=require("bcryptjs");
const {db,initCms}=require("../src/db/cms");
initCms();

const rl=readline.createInterface({input:process.stdin,output:process.stdout});
const ask=q=>new Promise(r=>rl.question(q,r));

(async()=>{
  const username=(await ask("Admin username: ")).trim();
  const password=await ask("Admin password: ");
  if(username.length<3 || password.length<10) {
    console.error("Use a username >=3 chars and password >=10 chars.");
    process.exitCode=1; rl.close(); return;
  }
  const hash=await bcrypt.hash(password,12);
  db.prepare("INSERT INTO admins(username,password_hash) VALUES(?,?)").run(username,hash);
  console.log("Admin created.");
  rl.close();
})();
