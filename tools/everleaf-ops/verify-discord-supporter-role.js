const fs = require("fs");

const [webRoot, envPath] = process.argv.slice(2);
const values=Object.fromEntries(fs.readFileSync(envPath,"utf8").split(/\r?\n/).filter(line=>line&&!line.startsWith("#")&&line.includes("=")).map(line=>[line.slice(0,line.indexOf("=")),line.slice(line.indexOf("=")+1)]));
const {db}=require(`${webRoot}/src/db/cms`);
const profile=db.prepare("SELECT discord_user_id FROM supporter_profiles WHERE discord_user_id <> '' ORDER BY updated_at DESC LIMIT 1").get();
if(!profile) throw new Error("No linked Discord profile found.");
(async()=>{
  const response=await fetch(`https://discord.com/api/v10/guilds/${values.DISCORD_GUILD_ID}/members/${profile.discord_user_id}`,{headers:{Authorization:`Bot ${values.DISCORD_BOT_TOKEN}`}});
  if(!response.ok) throw new Error(`Discord API returned ${response.status}.`);
  const member=await response.json();
  console.log(`supporter_role=${member.roles.includes(values.DISCORD_SUPPORTER_ROLE_ID)?"assigned":"missing"}`);
})().catch(error=>{console.error(error.message);process.exitCode=1;});
