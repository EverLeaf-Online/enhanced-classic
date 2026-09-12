# EverLeaf v180 gameplay UI visual overlay.
# Only overlays v180 assets that map cleanly onto existing v83 runtime behavior.
# StatusBar2/3 require native-client layout work and are intentionally excluded here.
# TRADE/FM artwork is intentionally preserved until the final HUD direction is chosen.

image:BuffIcon.img
image:GuildBBS.img
image:GuildMark.img
image:ChatBalloon.img
image:NameTag.img

# Language-neutral shared controls.
property:Basic.img/Cursor
property:Basic.img/CheckBox
property:Basic.img/HScr
property:Basic.img/HScr2
property:Basic.img/HScr3
property:Basic.img/HScr4
property:Basic.img/HScr5
property:Basic.img/VScr
property:Basic.img/VScr2
property:Basic.img/VScr3
property:Basic.img/VScr4
property:Basic.img/VScr5
property:Basic.img/VScr8
property:Basic.img/BtOK
property:Basic.img/BtCancel
property:Basic.img/BtYes
property:Basic.img/BtYes2
property:Basic.img/BtNo
property:Basic.img/BtNo2
property:Basic.img/BtComboBox
property:Basic.img/Notice
property:Basic.img/Notice2
property:Basic.img/Notice3
property:Basic.img/Notice4
property:Basic.img/YesNo
property:Basic.img/YesNo2
property:Basic.img/YesNo3
property:Basic.img/Tab
property:Basic.img/Tab2
property:Basic.img/Tab3
property:Basic.img/Tab4
property:Basic.img/Tab5
property:Basic.img/ItemNo
property:Basic.img/dcMark
property:Basic.img/LevelNo
property:Basic.img/BtMin
property:Basic.img/BtMin2
property:Basic.img/BtMax
property:Basic.img/BtMax2
property:Basic.img/BtOK2
property:Basic.img/BtCancel2
property:Basic.img/BtUP
property:Basic.img/BtDown
property:Basic.img/BtHide
property:Basic.img/BtHide2
property:Basic.img/BtClose
property:Basic.img/BtClose2
property:Basic.img/BtClaim
property:Basic.img/ComboBox
property:Basic.img/ComboBox2
property:Basic.img/ComboBox3
property:Basic.img/BtOK3
property:Basic.img/BtCancel3
property:Basic.img/BtQGiveup
property:Basic.img/KeyDownBar
property:Basic.img/BtSend
property:Basic.img/BtReceive
property:Basic.img/BtDel
property:Basic.img/icon
property:Basic.img/BtCoin
property:Basic.img/Tab6
property:Basic.img/Tab7
property:Basic.img/BtDecide
property:Basic.img/KeyDownBar1
property:Basic.img/BtHide3
property:Basic.img/BtMacro
property:Basic.img/VScr6
property:Basic.img/HScr6
property:Basic.img/ComboBox4
property:Basic.img/PQuestRank
property:Basic.img/ShowLevel
property:Basic.img/Notice5
property:Basic.img/ComboBox5

# Existing v83 windows with compatible path trees.
# UserList is excluded because v180 inserted/reordered social tabs, which shifts
# Guild/GuildAlliance content on the v83 client. KeyConfig is excluded because
# the donor has baked Korean labels. CashShop is excluded for the same reason.
property:UIWindow.img/MiniMap
property:UIWindow.img/ToolTip
property:UIWindow.img/Minigame
property:UIWindow.img/ShortCut
property:UIWindow.img/Skill
property:UIWindow.img/Stat
property:UIWindow.img/Item
property:UIWindow.img/Equip
property:UIWindow.img/Channel
property:UIWindow.img/Quest
property:UIWindow.img/QuestAlarm
property:UIWindow.img/GameMenu
property:UIWindow.img/UserInfo
property:UIWindow.img/Messenger
property:UIWindow.img/Trunk
property:UIWindow.img/WorldMap
