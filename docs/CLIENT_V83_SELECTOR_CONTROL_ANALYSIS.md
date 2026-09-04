# v83 selector control analysis

- scanned: `0x00500000`..`0x00700000`
- decoded instructions: 665881
- instructions touching CLogin/race displacement `+0x214`: 76

## Candidate near `0x00528E6D`
```asm
00528E16: push    4
00528E18: lea     eax, [esi + 0x17c]
00528E1E: push    eax
00528E1F: mov     byte ptr [ebp - 4], 6
00528E23: call    0xa61a3e
00528E28: mov     dword ptr [esi + 0x1c4], edi
00528E2E: mov     dword ptr [esi + 0x1cc], edi
00528E34: mov     dword ptr [esi + 0x1e4], edi
00528E3A: lea     eax, [esi + 0x200]
00528E40: mov     dword ptr [esi + 0x1e8], edi
00528E46: mov     dword ptr [esi + 0x1ec], edi
00528E4C: mov     dword ptr [esi + 0x1f4], edi
00528E52: mov     dword ptr [esi + 0x1f8], edi
00528E58: mov     dword ptr [esi + 0x1fc], edi
00528E5E: mov     dword ptr [eax + 8], edi
00528E61: mov     dword ptr [eax + 0xc], edi
00528E64: mov     dword ptr [eax + 0x10], edi
00528E67: mov     dword ptr [eax], 0xaf44f4
00528E6D: mov     dword ptr [esi + 0x214], edi
00528E73: mov     dword ptr [esi + 0x218], edi
00528E79: mov     dword ptr [esi + 0x21c], edi
00528E7F: mov     dword ptr [esi + 0x220], edi
00528E85: mov     dword ptr [esi + 0x224], edi
00528E8B: mov     dword ptr [esi + 0x234], edi
00528E91: mov     dword ptr [esi + 0x238], edi
00528E97: lea     ecx, [esi + 0x240]
00528E9D: mov     byte ptr [ebp - 4], 0xd
00528EA1: mov     dword ptr [esi + 0x23c], edi
00528EA7: call    0x8e49b5
00528EAC: mov     dword ptr [esi + 0x754], edi
00528EB2: mov     dword ptr [esi + 0x758], edi
00528EB8: lea     eax, [esi + 0x75c]
00528EBE: mov     dword ptr [eax + 8], edi
00528EC1: mov     dword ptr [eax + 0xc], edi
00528EC4: mov     dword ptr [eax + 0x10], edi
00528EC7: mov     dword ptr [eax], 0xaf44f0
00528ECD: lea     ecx, [esi + 0x770]
00528ED3: mov     byte ptr [ebp - 4], 0x11
00528ED7: call    0x528f5b
00528EDC: lea     eax, [esi + 0x79c]
00528EE2: mov     dword ptr [eax + 8], edi
00528EE5: mov     dword ptr [eax + 0xc], edi
00528EE8: mov     dword ptr [eax + 0x10], edi
00528EEB: mov     dword ptr [eax], 0xaf1218
00528EF1: mov     dword ptr [esi + 0x7b0], edi
00528EF7: call    dword ptr [0xaf0344]
```

## Candidate near `0x0052B96B`
```asm
0052B935: mov     ecx, dword ptr [esp + 8]
0052B939: mov     dword ptr [eax + 4], ecx
0052B93C: ret     8
0052B93F: mov     eax, 0xa8ab6b
0052B944: call    0xa60b98
0052B949: sub     esp, 0x84
0052B94F: push    ebx
0052B950: push    esi
0052B951: mov     esi, ecx
0052B953: lea     ebx, [esi + 0x200]
0052B959: push    edi
0052B95A: mov     ecx, ebx
0052B95C: call    0x5397e6
0052B961: call    0x987257
0052B966: xor     edi, edi
0052B968: push    edi
0052B969: push    edi
0052B96A: push    ecx
0052B96B: mov     dword ptr [esi + 0x214], eax
0052B971: mov     eax, esp
0052B973: mov     dword ptr [ebp - 0x1c], esp
0052B976: push    0x110c
0052B97B: push    eax
0052B97C: call    0x79e805
0052B981: mov     ecx, eax
0052B983: call    0x406292
0052B988: or      dword ptr [ebp - 4], 0xffffffff
0052B98C: lea     eax, [ebp - 0x80]
0052B98F: push    eax
0052B990: lea     ecx, [esi + 0x30]
0052B993: call    0x40263b
0052B998: mov     ecx, eax
0052B99A: call    0x403935
0052B99F: mov     ecx, eax
0052B9A1: mov     dword ptr [ebp - 4], 1
0052B9A8: call    0x4032b2
0052B9AD: cmp     eax, edi
0052B9AF: mov     dword ptr [ebp - 0x20], eax
0052B9B2: mov     dword ptr [ebp - 0x14], edi
0052B9B5: je      0x52b9d4
0052B9B7: lea     eax, [ebp - 0x20]
0052B9BA: push    eax
0052B9BB: lea     ecx, [ebp - 0x14]
0052B9BE: call    0x4052ad
0052B9C3: cmp     eax, edi
0052B9C5: jge     0x52b9d4
```

## Candidate near `0x00531BF8`
```asm
00531BAA: call    0xa03350
00531BAF: mov     eax, dword ptr [esi + 0x220]
00531BB5: test    eax, eax
00531BB7: je      0x531bdd
00531BB9: lea     edi, [esi + 0x228]
00531BBF: call    dword ptr [0xbf060c]
00531BC5: sub     eax, dword ptr [edi]
00531BC7: cmp     eax, 0xbb8
00531BCC: jbe     0x531bdd
00531BCE: and     dword ptr [esi + 0x220], 0
00531BD5: call    dword ptr [0xbf060c]
00531BDB: mov     dword ptr [edi], eax
00531BDD: call    0x987257
00531BE2: mov     edi, dword ptr [esi + 0x20c]
00531BE8: mov     ebx, eax
00531BEA: mov     eax, dword ptr [0xbe7918]
00531BEF: mov     eax, dword ptr [eax + 0x37ec]
00531BF5: mov     dword ptr [ebp - 0x14], ebx
00531BF8: sub     ebx, dword ptr [esi + 0x214]
00531BFE: mov     dword ptr [ebp - 0x18], eax
00531C01: test    edi, edi
00531C03: je      0x531c8a
00531C09: mov     ecx, edi
00531C0B: mov     eax, edi
00531C0D: mov     dword ptr [ebp - 0x10], edi
00531C10: add     edi, -0x10
00531C13: neg     eax
00531C15: sbb     eax, eax
00531C17: and     eax, edi
00531C19: mov     eax, dword ptr [eax + 4]
00531C1C: mov     edx, eax
00531C1E: add     eax, 0x10
00531C21: neg     edx
00531C23: sbb     edx, edx
00531C25: and     edx, eax
00531C27: push    ecx
00531C28: lea     ecx, [ebp - 0x34]
00531C2B: mov     edi, edx
00531C2D: call    0x531dd3
00531C32: and     dword ptr [ebp - 4], 0
00531C36: cmp     dword ptr [ebp - 0x2c], 1
00531C3A: jne     0x531c42
00531C3C: cmp     dword ptr [ebp - 0x18], 0
00531C40: jne     0x531c62
00531C42: cmp     ebx, dword ptr [ebp - 0x34]
00531C45: jl      0x531c70
```

## Candidate near `0x005E12DC`
```asm
005E129D: call    0xa60b98
005E12A2: push    ecx
005E12A3: push    esi
005E12A4: push    edi
005E12A5: mov     esi, ecx
005E12A7: xor     edi, edi
005E12A9: mov     dword ptr [ebp - 0x10], esi
005E12AC: mov     dword ptr [esi + 0x10], edi
005E12AF: mov     dword ptr [ebp - 4], edi
005E12B2: mov     dword ptr [esi + 0x14], edi
005E12B5: mov     dword ptr [esi + 0x7c], edi
005E12B8: lea     ecx, [esi + 0x1e0]
005E12BE: mov     byte ptr [ebp - 4], 2
005E12C2: call    0x873a21
005E12C7: mov     ecx, dword ptr [ebp - 0xc]
005E12CA: mov     dword ptr [esi + 0x1fc], edi
005E12D0: mov     dword ptr [esi + 0x200], edi
005E12D6: mov     dword ptr [esi + 0x208], edi
005E12DC: mov     dword ptr [esi + 0x214], edi
005E12E2: mov     dword ptr [esi + 0x218], edi
005E12E8: mov     dword ptr [esi + 0x21c], edi
005E12EE: mov     dword ptr [esi + 0x20c], 0xaf6768
005E12F8: lea     eax, [esi + 0x20c]
005E12FE: lea     eax, [esi + 0x220]
005E1304: mov     dword ptr [eax + 4], edi
005E1307: mov     dword ptr [eax + 0xc], edi
005E130A: mov     dword ptr [eax + 8], 0x1f
005E1311: mov     dword ptr [eax], 0xaf2074
005E1317: mov     dword ptr [eax + 0x10], 0x64
005E131E: mov     dword ptr [eax + 0x14], 0x18
005E1325: mov     dword ptr [esi + 0x238], edi
005E132B: pop     edi
005E132C: mov     eax, esi
005E132E: pop     esi
005E132F: mov     dword ptr fs:[0], ecx
005E1336: leave   
005E1337: ret     
005E1338: push    esi
005E1339: mov     esi, ecx
005E133B: call    0x5e1913
005E1340: test    byte ptr [esp + 8], 1
005E1345: je      0x5e1353
005E1347: mov     ecx, dword ptr [0xbf6be4]
005E134D: push    esi
005E134E: call    0x5df0f0
005E1353: mov     eax, esi
```

## Candidate near `0x005F3DBE`
```asm
005F3D5F: mov     dword ptr [esi + 0x1d8], ebx
005F3D65: mov     dword ptr [esi + 0x1e0], ebx
005F3D6B: mov     dword ptr [esi + 0x1e8], ebx
005F3D71: mov     dword ptr [esi + 0x1f0], ebx
005F3D77: mov     dword ptr [esi + 0x1f8], ebx
005F3D7D: mov     dword ptr [esi + 0x1fc], ebx
005F3D83: mov     dword ptr [esi + 0x200], ebx
005F3D89: mov     dword ptr [esi + 0x204], ebx
005F3D8F: mov     dword ptr [esi + 0x208], 0xfe
005F3D99: mov     dword ptr [esi + 0x20c], ebx
005F3D9F: mov     dword ptr [esi + 0x210], ebx
005F3DA5: push    0x4062df
005F3DAA: push    0x4a9cde
005F3DAF: push    5
005F3DB1: push    4
005F3DB3: lea     eax, [esi + 0x218]
005F3DB9: push    eax
005F3DBA: mov     byte ptr [ebp - 4], 0x1a
005F3DBE: mov     dword ptr [esi + 0x214], ebx
005F3DC4: call    0xa61a3e
005F3DC9: mov     byte ptr [esi + 0x234], bl
005F3DCF: mov     dword ptr [esi + 0x240], ebx
005F3DD5: mov     ebx, 0x5fd8ec
005F3DDA: push    ebx
005F3DDB: mov     edi, 0x5fd8e6
005F3DE0: push    edi
005F3DE1: push    9
005F3DE3: push    4
005F3DE5: lea     eax, [esi + 0x244]
005F3DEB: push    eax
005F3DEC: mov     byte ptr [ebp - 4], 0x1c
005F3DF0: call    0xa61a3e
005F3DF5: push    ebx
005F3DF6: push    edi
005F3DF7: push    9
005F3DF9: push    4
005F3DFB: lea     eax, [esi + 0x268]
005F3E01: push    eax
005F3E02: mov     byte ptr [ebp - 4], 0x1d
005F3E06: call    0xa61a3e
005F3E0B: mov     ecx, dword ptr [ebp - 0xc]
005F3E0E: pop     edi
005F3E0F: mov     dword ptr [esi], 0xaf6b24
005F3E15: mov     dword ptr [esi + 4], 0xaf6ad8
005F3E1C: mov     dword ptr [esi + 8], 0xaf6ad4
005F3E23: mov     dword ptr [esi + 0xc], 0xaf6ad0
```

## Candidate near `0x005F4E15`
```asm
005F4DE2: mov     eax, dword ptr [0xbeda44]
005F4DE7: cmp     eax, ebx
005F4DE9: je      0x5f4df4
005F4DEB: lea     ecx, [eax + 8]
005F4DEE: mov     eax, dword ptr [ecx]
005F4DF0: push    1
005F4DF2: call    dword ptr [eax]
005F4DF4: mov     ecx, dword ptr [0xbeda40]
005F4DFA: cmp     ecx, ebx
005F4DFC: je      0x5f4e15
005F4DFE: call    0x9e00af
005F4E03: mov     eax, dword ptr [0xbeda40]
005F4E08: cmp     eax, ebx
005F4E0A: je      0x5f4e15
005F4E0C: lea     ecx, [eax + 8]
005F4E0F: mov     eax, dword ptr [ecx]
005F4E11: push    1
005F4E13: call    dword ptr [eax]
005F4E15: mov     eax, dword ptr [esi + 0x214]
005F4E1B: sub     eax, ebx
005F4E1D: je      0x5f4ea3
005F4E23: dec     eax
005F4E24: je      0x5f4e68
005F4E26: dec     eax
005F4E27: jne     0x5f50e7
005F4E2D: cmp     dword ptr [0xbeda34], ebx
005F4E33: je      0x5f4e3a
005F4E35: call    0x5fd8ff
005F4E3A: push    0x138
005F4E3F: mov     ecx, 0xbf0b00
005F4E44: call    0x403065
005F4E49: mov     ecx, eax
005F4E4B: mov     dword ptr [ebp - 0x14], ecx
005F4E4E: cmp     ecx, ebx
005F4E50: mov     dword ptr [ebp - 4], 7
005F4E57: je      0x5f50e3
005F4E5D: push    esi
005F4E5E: call    0x619a66
005F4E63: jmp     0x5f50e3
005F4E68: cmp     dword ptr [0xbeda34], ebx
005F4E6E: je      0x5f4e75
005F4E70: call    0x5fd8ff
005F4E75: push    0x138
005F4E7A: mov     ecx, 0xbf0b00
005F4E7F: call    0x403065
005F4E84: mov     ecx, eax
```

## Candidate near `0x005F4F26`
```asm
005F4EFB: mov     eax, dword ptr [ecx]
005F4EFD: pop     edi
005F4EFE: push    edi
005F4EFF: call    dword ptr [eax]
005F4F01: jmp     0x5f4f06
005F4F03: push    1
005F4F05: pop     edi
005F4F06: mov     ecx, dword ptr [0xbeda34]
005F4F0C: cmp     ecx, ebx
005F4F0E: je      0x5f4f26
005F4F10: call    0x9e00af
005F4F15: mov     eax, dword ptr [0xbeda34]
005F4F1A: cmp     eax, ebx
005F4F1C: je      0x5f4f26
005F4F1E: lea     ecx, [eax + 8]
005F4F21: mov     eax, dword ptr [ecx]
005F4F23: push    edi
005F4F24: call    dword ptr [eax]
005F4F26: mov     eax, dword ptr [esi + 0x214]
005F4F2C: sub     eax, ebx
005F4F2E: je      0x5f505e
005F4F34: dec     eax
005F4F35: je      0x5f4fd0
005F4F3B: dec     eax
005F4F3C: jne     0x5f4fd0
005F4F42: mov     ecx, dword ptr [0xbeda48]
005F4F48: cmp     ecx, ebx
005F4F4A: je      0x5f4f62
005F4F4C: call    0x9e00af
005F4F51: mov     eax, dword ptr [0xbeda48]
005F4F56: cmp     eax, ebx
005F4F58: je      0x5f4f62
005F4F5A: lea     ecx, [eax + 8]
005F4F5D: mov     eax, dword ptr [ecx]
005F4F5F: push    edi
005F4F60: call    dword ptr [eax]
005F4F62: mov     ecx, dword ptr [0xbeda44]
005F4F68: cmp     ecx, ebx
005F4F6A: je      0x5f4f82
005F4F6C: call    0x9e00af
005F4F71: mov     eax, dword ptr [0xbeda44]
005F4F76: cmp     eax, ebx
005F4F78: je      0x5f4f82
005F4F7A: lea     ecx, [eax + 8]
005F4F7D: mov     eax, dword ptr [ecx]
005F4F7F: push    edi
```

## Candidate near `0x005F5592`
```asm
005F5542: lea     ecx, [ebp - 0x14]
005F5545: mov     dword ptr [ebp - 0x14], ebx
005F5548: call    0x414617
005F554D: lea     eax, [ebp - 0x14]
005F5550: push    eax
005F5551: lea     ecx, [esi + 0x240]
005F5557: mov     dword ptr [ebp - 4], 3
005F555E: call    0x4181c9
005F5563: or      dword ptr [ebp - 4], 0xffffffff
005F5567: lea     ecx, [ebp - 0x14]
005F556A: call    0x4062df
005F556F: mov     ecx, esi
005F5571: call    0x5fcf8a
005F5576: lea     ecx, [ebp - 0x260]
005F557C: call    0x43af1d
005F5581: mov     eax, dword ptr [0xbe7918]
005F5586: mov     eax, dword ptr [eax + 0x202c]
005F558C: mov     byte ptr [ebp - 0x254], al
005F5592: mov     eax, dword ptr [esi + 0x214]
005F5598: cmp     eax, ebx
005F559A: mov     dword ptr [ebp - 4], edi
005F559D: jne     0x5f55ab
005F559F: mov     dword ptr [ebp - 0x253], 0xa
005F55A9: jmp     0x5f55ba
005F55AB: cmp     eax, 2
005F55AE: jne     0x5f55ba
005F55B0: mov     dword ptr [ebp - 0x253], 0xb
005F55BA: lea     eax, [ebp - 0x260]
005F55C0: push    eax
005F55C1: mov     ecx, esi
005F55C3: call    0x5fd2e8
005F55C8: lea     edi, [esi + 0x1d4]
005F55CE: mov     ecx, edi
005F55D0: call    0x428967
005F55D5: push    ebx
005F55D6: push    0x64
005F55D8: mov     ecx, esi
005F55DA: call    0x5f595b
005F55DF: imul    eax, eax, 0x258
005F55E5: mov     ecx, 0xfffff6bf
005F55EA: sub     ecx, eax
005F55EC: push    ecx
005F55ED: push    0x16
005F55EF: push    ebx
005F55F0: push    ecx
005F55F1: mov     ecx, esp
```

## Candidate near `0x005F569D`
```asm
005F5662: call    0x403065
005F5667: mov     ecx, eax
005F5669: mov     dword ptr [ebp - 0x24], ecx
005F566C: cmp     ecx, ebx
005F566E: mov     dword ptr [ebp - 4], 2
005F5675: je      0x5f567d
005F5677: push    esi
005F5678: call    0x615596
005F567D: or      dword ptr [ebp - 4], 0xffffffff
005F5681: mov     eax, dword ptr [0xbeda6c]
005F5686: mov     ecx, eax
005F5688: add     eax, 4
005F568B: neg     ecx
005F568D: sbb     ecx, ecx
005F568F: and     ecx, eax
005F5691: push    ecx
005F5692: mov     ecx, dword ptr [0xbec20c]
005F5698: call    0x9e3264
005F569D: mov     dword ptr [esi + 0x214], 1
005F56A7: jmp     0x5f5826
005F56AC: mov     ecx, dword ptr [0xbec20c]
005F56B2: cmp     ecx, ebx
005F56B4: je      0x5f56d0
005F56B6: mov     eax, dword ptr [0xbeda4c]
005F56BB: cmp     eax, ebx
005F56BD: je      0x5f56d0
005F56BF: mov     edx, eax
005F56C1: add     eax, 4
005F56C4: neg     edx
005F56C6: sbb     edx, edx
005F56C8: and     edx, eax
005F56CA: push    edx
005F56CB: call    0x9e3264
005F56D0: mov     dword ptr [esi + 0x214], ebx
005F56D6: jmp     0x5f5826
005F56DB: or      dword ptr [esi + 0x190], 0xffffffff
005F56E2: lea     eax, [ebp + 0xb]
005F56E5: push    eax
005F56E6: push    0xf
005F56E8: lea     ecx, [esi + 0x194]
005F56EE: call    0x5fdd2d
005F56F3: lea     eax, [ebp - 0x1d]
005F56F6: push    eax
005F56F7: push    0xf
005F56F9: lea     ecx, [esi + 0x198]
005F56FF: call    0x5fdda6
```

## Candidate near `0x005F56D0`
```asm
005F5691: push    ecx
005F5692: mov     ecx, dword ptr [0xbec20c]
005F5698: call    0x9e3264
005F569D: mov     dword ptr [esi + 0x214], 1
005F56A7: jmp     0x5f5826
005F56AC: mov     ecx, dword ptr [0xbec20c]
005F56B2: cmp     ecx, ebx
005F56B4: je      0x5f56d0
005F56B6: mov     eax, dword ptr [0xbeda4c]
005F56BB: cmp     eax, ebx
005F56BD: je      0x5f56d0
005F56BF: mov     edx, eax
005F56C1: add     eax, 4
005F56C4: neg     edx
005F56C6: sbb     edx, edx
005F56C8: and     edx, eax
005F56CA: push    edx
005F56CB: call    0x9e3264
005F56D0: mov     dword ptr [esi + 0x214], ebx
005F56D6: jmp     0x5f5826
005F56DB: or      dword ptr [esi + 0x190], 0xffffffff
005F56E2: lea     eax, [ebp + 0xb]
005F56E5: push    eax
005F56E6: push    0xf
005F56E8: lea     ecx, [esi + 0x194]
005F56EE: call    0x5fdd2d
005F56F3: lea     eax, [ebp - 0x1d]
005F56F6: push    eax
005F56F7: push    0xf
005F56F9: lea     ecx, [esi + 0x198]
005F56FF: call    0x5fdda6
005F5704: lea     eax, [ebp - 0x1f]
005F5707: push    eax
005F5708: push    0xf
005F570A: lea     ecx, [esi + 0x19c]
005F5710: call    0x5fdc2a
005F5715: lea     eax, [ebp - 0x1e]
005F5718: push    eax
005F5719: push    0x3c
005F571B: lea     ecx, [esi + 0x138]
005F5721: call    0x5fdd2d
005F5726: lea     eax, [ebp - 0x20]
005F5729: push    eax
005F572A: push    0x3c
005F572C: lea     ecx, [esi + 0x13c]
005F5732: call    0x5fdda6
```

## Candidate near `0x005F5809`
```asm
005F57C1: cmp     dword ptr [ebp - 0x10], 5
005F57C5: jne     0x5f57ce
005F57C7: mov     ecx, esi
005F57C9: call    0x5fb155
005F57CE: mov     ecx, dword ptr [0xbec20c]
005F57D4: cmp     ecx, ebx
005F57D6: je      0x5f56d0
005F57DC: mov     eax, dword ptr [0xbeda68]
005F57E1: cmp     eax, ebx
005F57E3: jne     0x5f56bf
005F57E9: mov     eax, dword ptr [0xbeda5c]
005F57EE: jmp     0x5f56bb
005F57F3: mov     dword ptr [esi + 0x170], ebx
005F57F9: mov     ecx, dword ptr [esi + 0x1f0]
005F57FF: cmp     ecx, ebx
005F5801: je      0x5f5809
005F5803: push    ebx
005F5804: call    0x51fb4e
005F5809: mov     dword ptr [esi + 0x214], ebx
005F580F: mov     eax, dword ptr [0xbe7b38]
005F5814: cmp     dword ptr [eax + 0x24], 2
005F5818: jne     0x5f5826
005F581A: call    0x5fd982
005F581F: mov     ecx, eax
005F5821: call    0x6bf60f
005F5826: push    dword ptr [ebp - 0x10]
005F5829: mov     ecx, esi
005F582B: call    0x5fc0e4
005F5830: push    dword ptr [esi + 0x168]
005F5836: mov     ecx, esi
005F5838: mov     dword ptr [ebp + 8], eax
005F583B: call    0x5fc0e4
005F5840: cmp     dword ptr [ebp - 0x10], 5
005F5844: mov     dword ptr [ebp - 0x14], eax
005F5847: jne     0x5f5855
005F5849: push    1
005F584B: mov     ecx, esi
005F584D: call    0x5fc0e4
005F5852: mov     dword ptr [ebp + 8], eax
005F5855: cmp     dword ptr [esi + 0x168], 5
005F585C: jne     0x5f586a
005F585E: push    1
005F5860: mov     ecx, esi
005F5862: call    0x5fc0e4
005F5867: mov     dword ptr [ebp - 0x14], eax
005F586A: mov     eax, dword ptr [ebp - 0x14]
```

## Candidate near `0x005F595B`
```asm
005F5922: push    eax
005F5923: call    0x79e805
005F5928: mov     ecx, eax
005F592A: call    0x406276
005F592F: push    dword ptr [eax]
005F5931: mov     dword ptr [ebp - 4], 8
005F5938: call    0x989588
005F593D: or      dword ptr [ebp - 4], 0xffffffff
005F5941: pop     ecx
005F5942: lea     ecx, [ebp - 0x1c]
005F5945: call    0x40265e
005F594A: mov     ecx, dword ptr [ebp - 0xc]
005F594D: pop     edi
005F594E: pop     esi
005F594F: mov     dword ptr fs:[0], ecx
005F5956: pop     ebx
005F5957: leave   
005F5958: ret     4
005F595B: mov     eax, dword ptr [ecx + 0x214]
005F5961: ret     
005F5962: mov     eax, 0xa977c8
005F5967: call    0xa60b98
005F596C: push    ecx
005F596D: push    ecx
005F596E: push    ebx
005F596F: push    esi
005F5970: mov     esi, ecx
005F5972: mov     eax, dword ptr [esi + 0x168]
005F5978: push    edi
005F5979: xor     edi, edi
005F597B: sub     eax, edi
005F597D: mov     dword ptr [ebp - 0x10], esi
005F5980: je      0x5f625a
005F5986: dec     eax
005F5987: je      0x5f60cc
005F598D: dec     eax
005F598E: je      0x5f5ec9
005F5994: dec     eax
005F5995: je      0x5f5c9d
005F599B: dec     eax
005F599C: je      0x5f5aee
005F59A2: dec     eax
005F59A3: jne     0x5f6416
005F59A9: mov     ecx, dword ptr [0xbeda5c]
005F59AF: cmp     ecx, edi
005F59B1: push    1
```

## Candidate near `0x005F6410`
```asm
005F63DA: push    ebx
005F63DB: call    dword ptr [eax]
005F63DD: mov     ecx, dword ptr [0xbeda6c]
005F63E3: cmp     ecx, edi
005F63E5: je      0x5f63fd
005F63E7: call    0x9e00af
005F63EC: mov     eax, dword ptr [0xbeda6c]
005F63F1: cmp     eax, edi
005F63F3: je      0x5f63fd
005F63F5: lea     ecx, [eax + 8]
005F63F8: mov     eax, dword ptr [ecx]
005F63FA: push    ebx
005F63FB: call    dword ptr [eax]
005F63FD: push    edi
005F63FE: mov     ecx, esi
005F6400: call    0x5fc313
005F6405: lea     ecx, [esi + 0x1d4]
005F640B: call    0x5fd9e2
005F6410: mov     dword ptr [esi + 0x214], edi
005F6416: mov     ecx, dword ptr [ebp - 0xc]
005F6419: pop     edi
005F641A: pop     esi
005F641B: pop     ebx
005F641C: mov     dword ptr fs:[0], ecx
005F6423: leave   
005F6424: ret     
005F6425: mov     eax, dword ptr [0xbe7918]
005F642A: mov     edx, dword ptr [eax + 0x2054]
005F6430: push    esi
005F6431: mov     esi, dword ptr [ecx + 0x18c]
005F6437: shl     edx, 5
005F643A: xor     eax, eax
005F643C: cmp     dword ptr [edx + esi + 0x18], eax
005F6440: je      0x5f644c
005F6442: push    eax
005F6443: push    0x24
005F6445: call    0x60f024
005F644A: jmp     0x5f6475
005F644C: mov     edx, dword ptr [ecx + 0x17c]
005F6452: mov     esi, dword ptr [ecx + 0x194]
005F6458: imul    edx, edx, 0x2ac
005F645E: cmp     dword ptr [edx + esi - 0x2ac], eax
005F6465: je      0x5f6479
005F6467: add     ecx, 0x1f4
005F646D: push    ecx
005F646E: push    9
```

## Candidate near `0x005F7F04`
```asm
005F7ED5: push    ebx
005F7ED6: push    0xa
005F7ED8: call    0x60f119
005F7EDD: pop     ecx
005F7EDE: pop     ecx
005F7EDF: jmp     0x5f7f51
005F7EE1: push    0x16
005F7EE3: lea     ecx, [ebp - 0x24]
005F7EE6: call    0x6ec9ce
005F7EEB: push    ecx
005F7EEC: mov     eax, esp
005F7EEE: mov     dword ptr [ebp - 0x14], esp
005F7EF1: push    eax
005F7EF2: mov     ecx, esi
005F7EF4: mov     dword ptr [ebp - 4], ebx
005F7EF7: call    0x5f7f60
005F7EFC: lea     ecx, [ebp - 0x24]
005F7EFF: call    0x46f3cf
005F7F04: push    dword ptr [esi + 0x214]
005F7F0A: lea     ecx, [ebp - 0x24]
005F7F0D: call    0x4065a6
005F7F12: push    ebx
005F7F13: mov     ecx, esi
005F7F15: call    0x5f7f84
005F7F1A: push    eax
005F7F1B: lea     ecx, [ebp - 0x24]
005F7F1E: call    0x4065a6
005F7F23: inc     ebx
005F7F24: cmp     ebx, 8
005F7F27: jl      0x5f7f12
005F7F29: xor     eax, eax
005F7F2B: mov     al, byte ptr [esi + 0x234]
005F7F31: lea     ecx, [ebp - 0x24]
005F7F34: push    eax
005F7F35: call    0x406549
005F7F3A: lea     eax, [ebp - 0x24]
005F7F3D: push    eax
005F7F3E: mov     ecx, esi
005F7F40: call    0x5f6932
005F7F45: or      dword ptr [ebp - 4], 0xffffffff
005F7F49: lea     ecx, [ebp - 0x20]
005F7F4C: call    0x428cf1
005F7F51: mov     ecx, dword ptr [ebp - 0xc]
005F7F54: pop     edi
005F7F55: pop     esi
005F7F56: mov     dword ptr fs:[0], ecx
```

## Candidate near `0x005FC0ED`
```asm
005FC0BB: call    dword ptr [ecx + 8]
005FC0BE: mov     eax, dword ptr [ebp - 0x1c]
005FC0C1: or      dword ptr [ebp - 4], 0xffffffff
005FC0C5: cmp     eax, ebx
005FC0C7: je      0x5fc0cf
005FC0C9: mov     ecx, dword ptr [eax]
005FC0CB: push    eax
005FC0CC: call    dword ptr [ecx + 8]
005FC0CF: mov     ecx, dword ptr [ebp - 0xc]
005FC0D2: lea     esp, [ebp - 0xbc]
005FC0D8: pop     edi
005FC0D9: pop     esi
005FC0DA: mov     dword ptr fs:[0], ecx
005FC0E1: pop     ebx
005FC0E2: leave   
005FC0E3: ret     
005FC0E4: cmp     dword ptr [ecx + 0x168], 4
005FC0EB: jne     0x5fc0f5
005FC0ED: mov     eax, dword ptr [ecx + 0x214]
005FC0F3: jmp     0x5fc0f7
005FC0F5: xor     eax, eax
005FC0F7: mov     ecx, dword ptr [esp + 4]
005FC0FB: add     ecx, eax
005FC0FD: imul    ecx, ecx, 0x258
005FC103: push    -8
005FC105: pop     eax
005FC106: sub     eax, ecx
005FC108: ret     4
005FC10B: push    esi
005FC10C: mov     esi, ecx
005FC10E: cmp     dword ptr [esi + 0x168], 4
005FC115: jne     0x5fc140
005FC117: mov     eax, dword ptr [esi + 0x1d8]
005FC11D: test    eax, eax
005FC11F: je      0x5fc140
005FC121: cmp     dword ptr [0xbeda34], 0
005FC128: je      0x5fc140
005FC12A: add     eax, 4
005FC12D: push    eax
005FC12E: call    0x5fd2e8
005FC133: mov     ecx, dword ptr [esi + 0x1d8]
005FC139: push    0
005FC13B: call    0x4515bd
005FC140: pop     esi
005FC141: ret     
005FC142: mov     eax, 0xa9807a
```

## Candidate near `0x005FCFBC`
```asm
005FCF8A: mov     eax, 0xa981e8
005FCF8F: call    0xa60b98
005FCF94: sub     esp, 0x10
005FCF97: push    ebx
005FCF98: push    esi
005FCF99: push    edi
005FCF9A: mov     edi, ecx
005FCF9C: lea     eax, [edi + 0x268]
005FCFA2: push    9
005FCFA4: mov     esi, eax
005FCFA6: pop     ebx
005FCFA7: lea     ecx, [esi - 0x24]
005FCFAA: call    0x5fe122
005FCFAF: mov     ecx, esi
005FCFB1: call    0x5fe122
005FCFB6: add     esi, 4
005FCFB9: dec     ebx
005FCFBA: jne     0x5fcfa7
005FCFBC: cmp     dword ptr [edi + 0x214], 2
005FCFC3: mov     eax, dword ptr [0xbe7918]
005FCFC8: mov     eax, dword ptr [eax + 0x202c]
005FCFCE: mov     byte ptr [edi + 0x234], al
005FCFD4: lea     eax, [edi + 0x1b4]
005FCFDA: je      0x5fcfe2
005FCFDC: lea     eax, [edi + 0x1a0]
005FCFE2: mov     esi, dword ptr [eax + 0xc]
005FCFE5: or      ebx, 0xffffffff
005FCFE8: test    esi, esi
005FCFEA: je      0x5fd0ae
005FCFF0: jmp     0x5fcff5
005FCFF2: mov     esi, dword ptr [ebp - 0x10]
005FCFF5: mov     eax, esi
005FCFF7: neg     eax
005FCFF9: sbb     eax, eax
005FCFFB: lea     ecx, [esi - 0x10]
005FCFFE: and     eax, ecx
005FD000: mov     eax, dword ptr [eax + 4]
005FD003: mov     ecx, eax
005FD005: add     eax, 0x10
005FD008: neg     ecx
005FD00A: sbb     ecx, ecx
005FD00C: and     ecx, eax
005FD00E: mov     eax, dword ptr [esi]
005FD010: test    eax, eax
005FD012: mov     dword ptr [ebp - 0x10], ecx
005FD015: jne     0x5fd058
```

## Candidate near `0x00616060`
```asm
0061602C: mov     byte ptr [ebp - 4], 0x2c
00616030: call    0x40265e
00616035: mov     eax, dword ptr [ebp - 0x18]
00616038: cmp     eax, edi
0061603A: mov     byte ptr [ebp - 4], 0x2b
0061603E: je      0x616046
00616040: mov     ecx, dword ptr [eax]
00616042: push    eax
00616043: call    dword ptr [ecx + 8]
00616046: mov     eax, dword ptr [ebp - 0x14]
00616049: cmp     eax, edi
0061604B: mov     byte ptr [ebp - 4], 3
0061604F: je      0x616057
00616051: mov     ecx, dword ptr [eax]
00616053: push    eax
00616054: call    dword ptr [ecx + 8]
00616057: mov     eax, dword ptr [ebx + 0x6c]
0061605A: mov     esi, dword ptr [0xaf0268]
00616060: mov     dword ptr [eax + 0x214], 1
0061606A: lea     eax, [ebp - 0x70]
0061606D: push    eax
0061606E: call    esi
00616070: mov     edi, 0xbf6300
00616075: lea     eax, [ebp - 0x70]
00616078: push    edi
00616079: push    eax
0061607A: call    0x402b8c
0061607F: test    eax, eax
00616081: pop     ecx
00616082: pop     ecx
00616083: jge     0x61608b
00616085: push    eax
00616086: call    0xa5fde4
0061608B: lea     eax, [ebp - 0x60]
0061608E: push    eax
0061608F: mov     byte ptr [ebp - 4], 0x31
00616093: call    esi
00616095: lea     eax, [ebp - 0x60]
00616098: push    edi
00616099: push    eax
0061609A: call    0x402b8c
0061609F: test    eax, eax
006160A1: pop     ecx
006160A2: pop     ecx
006160A3: jge     0x6160ab
006160A5: push    eax
```

## Candidate near `0x00617348`
```asm
00617314: call    0x40291d
00617319: test    eax, eax
0061731B: pop     ecx
0061731C: jge     0x617324
0061731E: push    eax
0061731F: call    0xa5fde4
00617324: or      dword ptr [ebp - 4], 0xffffffff
00617328: lea     eax, [ebp - 0xe4]
0061732E: push    eax
0061732F: call    0x40291d
00617334: pop     ecx
00617335: test    eax, eax
00617337: jge     0x61733f
00617339: push    eax
0061733A: call    0xa5fde4
0061733F: mov     eax, dword ptr [ebp + 8]
00617342: mov     dword ptr [ebx + 0x70], eax
00617345: mov     ebx, dword ptr [ebx + 0x6c]
00617348: mov     dword ptr [ebx + 0x214], eax
0061734E: lea     eax, [ebp + 8]
00617351: push    0x13f9
00617356: push    eax
00617357: call    0x79e805
0061735C: mov     ecx, eax
0061735E: call    0x406276
00617363: push    dword ptr [eax]
00617365: mov     dword ptr [ebp - 4], 0x45
0061736C: call    0x989588
00617371: or      dword ptr [ebp - 4], 0xffffffff
00617375: pop     ecx
00617376: lea     ecx, [ebp + 8]
00617379: call    0x40265e
0061737E: mov     ecx, dword ptr [ebp - 0xc]
00617381: pop     edi
00617382: pop     esi
00617383: mov     dword ptr fs:[0], ecx
0061738A: pop     ebx
0061738B: leave   
0061738C: ret     4
0061738F: push    esi
00617390: push    dword ptr [esp + 8]
00617394: mov     esi, ecx
00617396: mov     eax, dword ptr [esi]
00617398: push    esi
00617399: call    dword ptr [eax + 0xb4]
0061739F: test    eax, eax
```

## Candidate near `0x0061755C`
```asm
00617520: mov     eax, dword ptr [esp + 8]
00617524: sub     eax, 0xd
00617527: je      0x6175ae
0061752D: sub     eax, 0xe
00617530: je      0x61759b
00617532: sub     eax, 0xa
00617535: je      0x617574
00617537: dec     eax
00617538: dec     eax
00617539: jne     0x6175c1
0061753F: xor     eax, eax
00617541: cmp     dword ptr [ecx + 0x88], eax
00617547: jne     0x6175c1
00617549: cmp     dword ptr [ecx + 0x98], eax
0061754F: jne     0x6175c1
00617551: cmp     dword ptr [ecx + 0xa8], eax
00617557: jne     0x6175c1
00617559: mov     eax, dword ptr [ecx + 0x68]
0061755C: mov     eax, dword ptr [eax + 0x214]
00617562: inc     eax
00617563: push    3
00617565: cdq     
00617566: pop     esi
00617567: idiv    esi
00617569: add     ecx, -4
0061756C: push    edx
0061756D: call    0x616283
00617572: jmp     0x6175c1
00617574: xor     eax, eax
00617576: cmp     dword ptr [ecx + 0x88], eax
0061757C: jne     0x6175c1
0061757E: cmp     dword ptr [ecx + 0x98], eax
00617584: jne     0x6175c1
00617586: cmp     dword ptr [ecx + 0xa8], eax
0061758C: jne     0x6175c1
0061758E: mov     eax, dword ptr [ecx + 0x68]
00617591: mov     eax, dword ptr [eax + 0x214]
00617597: inc     eax
00617598: inc     eax
00617599: jmp     0x617563
0061759B: mov     ecx, dword ptr [ecx + 0x68]
0061759E: cmp     dword ptr [ecx + 0x16c], 0
006175A5: jne     0x6175c1
006175A7: call    0x5f9805
006175AC: jmp     0x6175c1
006175AE: mov     ecx, dword ptr [ecx + 0x68]
```

## Candidate near `0x00617591`
```asm
0061755C: mov     eax, dword ptr [eax + 0x214]
00617562: inc     eax
00617563: push    3
00617565: cdq     
00617566: pop     esi
00617567: idiv    esi
00617569: add     ecx, -4
0061756C: push    edx
0061756D: call    0x616283
00617572: jmp     0x6175c1
00617574: xor     eax, eax
00617576: cmp     dword ptr [ecx + 0x88], eax
0061757C: jne     0x6175c1
0061757E: cmp     dword ptr [ecx + 0x98], eax
00617584: jne     0x6175c1
00617586: cmp     dword ptr [ecx + 0xa8], eax
0061758C: jne     0x6175c1
0061758E: mov     eax, dword ptr [ecx + 0x68]
00617591: mov     eax, dword ptr [eax + 0x214]
00617597: inc     eax
00617598: inc     eax
00617599: jmp     0x617563
0061759B: mov     ecx, dword ptr [ecx + 0x68]
0061759E: cmp     dword ptr [ecx + 0x16c], 0
006175A5: jne     0x6175c1
006175A7: call    0x5f9805
006175AC: jmp     0x6175c1
006175AE: mov     ecx, dword ptr [ecx + 0x68]
006175B1: cmp     dword ptr [ecx + 0x16c], 0
006175B8: jne     0x6175c1
006175BA: push    -1
006175BC: call    0x5f53c0
006175C1: pop     esi
006175C2: ret     8
006175C5: cmp     dword ptr [esp + 4], 0
006175CA: je      0x6175de
006175CC: mov     edx, dword ptr [ecx + 0x68]
006175CF: lea     eax, [ecx - 4]
006175D2: neg     eax
006175D4: sbb     eax, eax
006175D6: and     eax, ecx
006175D8: mov     dword ptr [edx + 0x188], eax
006175DE: push    dword ptr [esp + 4]
006175E2: call    0x9e0369
006175E7: ret     4
006175EA: mov     eax, 0xa9a8cc
```

## Candidate near `0x00619151`
```asm
00619119: mov     eax, 0xa9ad8f
0061911E: call    0xa60b98
00619123: push    ecx
00619124: push    esi
00619125: push    edi
00619126: mov     edi, dword ptr [ebp + 8]
00619129: mov     esi, ecx
0061912B: push    edi
0061912C: mov     dword ptr [ebp - 0x10], esi
0061912F: call    0x618432
00619134: push    1
00619136: xor     eax, eax
00619138: push    eax
00619139: push    eax
0061913A: mov     dword ptr [ebp - 4], eax
0061913D: mov     dword ptr [esi], 0xaf777c
00619143: mov     dword ptr [esi + 4], 0xaf7730
0061914A: mov     dword ptr [esi + 8], 0xaf772c
00619151: mov     eax, dword ptr [edi + 0x214]
00619157: imul    eax, eax, 0x258
0061915D: push    0xa
0061915F: push    0x179
00619164: push    0xe1
00619169: mov     ecx, 0xfffff5cb
0061916E: sub     ecx, eax
00619170: push    ecx
00619171: push    0x6d
00619173: mov     ecx, esi
00619175: call    0x9de4d2
0061917A: mov     ecx, dword ptr [ebp - 0xc]
0061917D: pop     edi
0061917E: mov     eax, esi
00619180: pop     esi
00619181: mov     dword ptr fs:[0], ecx
00619188: leave   
00619189: ret     4
0061918C: push    esi
0061918D: mov     esi, ecx
0061918F: call    0x6191b0
00619194: test    byte ptr [esp + 8], 1
00619199: je      0x6191a9
0061919B: lea     eax, [esi - 8]
0061919E: push    eax
0061919F: mov     ecx, 0xbf0b00
006191A4: call    0x4031ed
006191A9: lea     eax, [esi - 8]
```

## Candidate near `0x0064D2F9`
```asm
0064D28D: mov     dword ptr [esi + 0x1bc], edi
0064D293: mov     dword ptr [esi + 0x1c4], edi
0064D299: mov     dword ptr [esi + 0x1cc], edi
0064D29F: mov     dword ptr [esi + 0x1d8], edi
0064D2A5: mov     dword ptr [esi + 0x1dc], edi
0064D2AB: mov     dword ptr [esi + 0x1e0], edi
0064D2B1: mov     dword ptr [esi + 0x1e4], edi
0064D2B7: mov     dword ptr [esi + 0x1e8], edi
0064D2BD: mov     dword ptr [esi + 0x1ec], edi
0064D2C3: mov     dword ptr [esi + 0x1f0], edi
0064D2C9: mov     dword ptr [esi + 0x1f4], edi
0064D2CF: mov     dword ptr [esi + 0x1f8], edi
0064D2D5: mov     dword ptr [esi + 0x1fc], edi
0064D2DB: mov     dword ptr [esi + 0x200], edi
0064D2E1: mov     dword ptr [esi + 0x204], edi
0064D2E7: mov     dword ptr [esi + 0x208], edi
0064D2ED: mov     dword ptr [esi + 0x20c], edi
0064D2F3: mov     dword ptr [esi + 0x210], edi
0064D2F9: mov     dword ptr [esi + 0x214], edi
0064D2FF: mov     dword ptr [esi + 0x218], edi
0064D305: lea     ecx, [esi + 0x21c]
0064D30B: mov     byte ptr [ebp - 4], 0x1b
0064D30F: call    0x8e49b5
0064D314: mov     dword ptr [esi + 0x744], edi
0064D31A: mov     dword ptr [esi + 0x754], edi
0064D320: mov     dword ptr [esi + 0x758], edi
0064D326: mov     byte ptr [ebp - 4], 0x1e
0064D32A: mov     dword ptr [esi + 0x824], edi
0064D330: call    0x987257
0064D335: mov     dword ptr [esi + 0x828], eax
0064D33B: mov     dword ptr [esi], 0xaf8028
0064D341: mov     dword ptr [esi + 4], 0xaf7fdc
0064D348: mov     dword ptr [esi + 8], 0xaf7fd8
0064D34F: push    0x600
0064D354: lea     eax, [ebp - 0x10]
0064D357: push    eax
0064D358: call    0x79e805
0064D35D: mov     ecx, eax
0064D35F: call    0x406276
0064D364: mov     eax, dword ptr [eax]
0064D366: push    edi
0064D367: push    1
0064D369: push    eax
0064D36A: mov     ecx, esi
0064D36C: mov     byte ptr [ebp - 4], 0x1f
0064D370: call    0x4edaef
```

## Candidate near `0x0064D911`
```asm
0064D8D5: mov     dword ptr [ebp - 0x10], esi
0064D8D8: mov     dword ptr [esi], 0xaf7fd8
0064D8DE: mov     eax, dword ptr [esi + 0x750]
0064D8E4: test    eax, eax
0064D8E6: mov     dword ptr [ebp - 4], 0x1d
0064D8ED: je      0x64d8f9
0064D8EF: add     eax, -0xc
0064D8F2: push    eax
0064D8F3: call    0x428d13
0064D8F8: pop     ecx
0064D8F9: mov     eax, dword ptr [esi + 0x74c]
0064D8FF: test    eax, eax
0064D901: mov     byte ptr [ebp - 4], 0x1c
0064D905: je      0x64d911
0064D907: add     eax, -0xc
0064D90A: push    eax
0064D90B: call    0x428d13
0064D910: pop     ecx
0064D911: lea     ecx, [esi + 0x214]
0064D917: mov     byte ptr [ebp - 4], 0x1b
0064D91B: call    0x8e6ba3
0064D920: lea     ecx, [esi + 0x210]
0064D926: call    0x45baee
0064D92B: lea     ecx, [esi + 0x20c]
0064D931: mov     byte ptr [ebp - 4], 0x19
0064D935: call    0x43443c
0064D93A: lea     ecx, [esi + 0x208]
0064D940: mov     byte ptr [ebp - 4], 0x18
0064D944: call    0x457245
0064D949: mov     eax, dword ptr [esi + 0x204]
0064D94F: test    eax, eax
0064D951: mov     byte ptr [ebp - 4], 0x17
0064D955: je      0x64d95d
0064D957: mov     ecx, dword ptr [eax]
0064D959: push    eax
0064D95A: call    dword ptr [ecx + 8]
0064D95D: mov     eax, dword ptr [esi + 0x200]
0064D963: test    eax, eax
0064D965: mov     byte ptr [ebp - 4], 0x16
0064D969: je      0x64d971
0064D96B: mov     ecx, dword ptr [eax]
0064D96D: push    eax
0064D96E: call    dword ptr [ecx + 8]
0064D971: mov     eax, dword ptr [esi + 0x1fc]
0064D977: test    eax, eax
0064D979: mov     byte ptr [ebp - 4], 0x15
```

## Candidate near `0x00653B2E`
```asm
00653AF6: mov     ebx, dword ptr [ebp + 8]
00653AF9: push    esi
00653AFA: push    edi
00653AFB: xor     esi, esi
00653AFD: cmp     ebx, esi
00653AFF: mov     edi, ecx
00653B01: mov     dword ptr [ebp - 0x14], edi
00653B04: jl      0x654265
00653B0A: cmp     ebx, dword ptr [edi + 0x780]
00653B10: jge     0x654265
00653B16: mov     dword ptr [ebp - 0x24], esi
00653B19: push    3
00653B1B: push    -2
00653B1D: lea     ecx, [ebp - 0x44]
00653B20: mov     dword ptr [ebp - 4], esi
00653B23: call    0x402fab
00653B28: shl     ebx, 2
00653B2B: mov     dword ptr [ebp - 0x18], ebx
00653B2E: add     ebx, dword ptr [edi + 0x214]
00653B34: mov     byte ptr [ebp - 4], 1
00653B38: cmp     dword ptr [ebx], esi
00653B3A: jne     0x653b46
00653B3C: push    0x80004003
00653B41: call    0xa5fde4
00653B46: mov     ecx, dword ptr [ebx]
00653B48: lea     eax, [ebp - 0x44]
00653B4B: push    eax
00653B4C: lea     eax, [ebp - 0x10]
00653B4F: push    eax
00653B50: call    0x4143fb
00653B55: lea     ecx, [ebp - 0x10]
00653B58: call    0x4156ab
00653B5D: and     byte ptr [ebp - 4], 0
00653B61: lea     eax, [ebp - 0x44]
00653B64: push    eax
00653B65: call    0x40291d
00653B6A: cmp     eax, esi
00653B6C: pop     ecx
00653B6D: jge     0x653b75
00653B6F: push    eax
00653B70: call    0xa5fde4
00653B75: lea     eax, [ebp - 0x10]
00653B78: push    0x158b
00653B7D: push    eax
00653B7E: call    0x79e805
00653B83: mov     ecx, eax
```

## Candidate near `0x00653CB2`
```asm
00653C7F: cmp     eax, esi
00653C81: mov     dword ptr [ebp - 0x48], eax
00653C84: mov     dword ptr [ebp - 0x10], esi
00653C87: je      0x653ca6
00653C89: lea     eax, [ebp - 0x48]
00653C8C: push    eax
00653C8D: lea     ecx, [ebp - 0x10]
00653C90: call    0x41e527
00653C95: cmp     eax, esi
00653C97: jge     0x653ca6
00653C99: cmp     eax, 0x80004002
00653C9E: je      0x653ca6
00653CA0: push    eax
00653CA1: call    0xa5fde4
00653CA6: mov     eax, dword ptr [ebp - 0x10]
00653CA9: mov     edi, dword ptr [ebp - 0x18]
00653CAC: mov     dword ptr [ebp - 0x1c], eax
00653CAF: mov     eax, dword ptr [ebp - 0x14]
00653CB2: add     edi, dword ptr [eax + 0x214]
00653CB8: mov     byte ptr [ebp - 4], 0xa
00653CBC: cmp     dword ptr [edi], esi
00653CBE: jne     0x653cca
00653CC0: push    0x80004003
00653CC5: call    0xa5fde4
00653CCA: mov     edi, dword ptr [edi]
00653CCC: lea     eax, [ebp - 0x34]
00653CCF: push    eax
00653CD0: lea     eax, [ebp - 0x58]
00653CD3: push    eax
00653CD4: lea     eax, [ebp - 0x68]
00653CD7: push    eax
00653CD8: lea     eax, [ebp - 0x78]
00653CDB: push    eax
00653CDC: lea     eax, [ebp - 0x44]
00653CDF: push    eax
00653CE0: push    dword ptr [ebp - 0x1c]
00653CE3: lea     eax, [ebp - 0x88]
00653CE9: push    eax
00653CEA: mov     ecx, edi
00653CEC: call    0x426bab
00653CF1: lea     eax, [ebp - 0x88]
00653CF7: push    eax
00653CF8: call    0x40291d
00653CFD: cmp     eax, esi
00653CFF: pop     ecx
00653D00: jge     0x653d08
```

## Candidate near `0x00653E80`
```asm
00653E4D: cmp     eax, esi
00653E4F: mov     dword ptr [ebp - 0x1c], eax
00653E52: mov     dword ptr [ebp - 0x10], esi
00653E55: je      0x653e74
00653E57: lea     eax, [ebp - 0x1c]
00653E5A: push    eax
00653E5B: lea     ecx, [ebp - 0x10]
00653E5E: call    0x41e527
00653E63: cmp     eax, esi
00653E65: jge     0x653e74
00653E67: cmp     eax, 0x80004002
00653E6C: je      0x653e74
00653E6E: push    eax
00653E6F: call    0xa5fde4
00653E74: mov     eax, dword ptr [ebp - 0x10]
00653E77: mov     edi, dword ptr [ebp - 0x18]
00653E7A: mov     dword ptr [ebp - 0x20], eax
00653E7D: mov     eax, dword ptr [ebp - 0x14]
00653E80: add     edi, dword ptr [eax + 0x214]
00653E86: mov     byte ptr [ebp - 4], 0x12
00653E8A: cmp     dword ptr [edi], esi
00653E8C: jne     0x653e98
00653E8E: push    0x80004003
00653E93: call    0xa5fde4
00653E98: mov     edi, dword ptr [edi]
00653E9A: lea     eax, [ebp - 0x44]
00653E9D: push    eax
00653E9E: lea     eax, [ebp - 0x78]
00653EA1: push    eax
00653EA2: lea     eax, [ebp - 0x68]
00653EA5: push    eax
00653EA6: lea     eax, [ebp - 0x58]
00653EA9: push    eax
00653EAA: lea     eax, [ebp - 0x34]
00653EAD: push    eax
00653EAE: push    dword ptr [ebp - 0x20]
00653EB1: lea     eax, [ebp - 0x98]
00653EB7: push    eax
00653EB8: mov     ecx, edi
00653EBA: call    0x426bab
00653EBF: lea     eax, [ebp - 0x98]
00653EC5: push    eax
00653EC6: call    0x40291d
00653ECB: cmp     eax, esi
00653ECD: pop     ecx
00653ECE: jge     0x653ed6
```

## Candidate near `0x00653F80`
```asm
00653F50: pop     ecx
00653F51: jge     0x653f59
00653F53: push    eax
00653F54: call    0xa5fde4
00653F59: and     byte ptr [ebp - 4], 0
00653F5D: lea     eax, [ebp - 0x44]
00653F60: push    eax
00653F61: call    0x40291d
00653F66: cmp     eax, esi
00653F68: pop     ecx
00653F69: jge     0x653f71
00653F6B: push    eax
00653F6C: call    0xa5fde4
00653F71: push    ebx
00653F72: lea     ecx, [ebp - 0x58]
00653F75: call    0x402f85
00653F7A: mov     edi, dword ptr [ebp - 0x18]
00653F7D: mov     eax, dword ptr [ebp - 0x14]
00653F80: add     edi, dword ptr [eax + 0x214]
00653F86: mov     byte ptr [ebp - 4], 0x13
00653F8A: cmp     dword ptr [edi], esi
00653F8C: jne     0x653f98
00653F8E: push    0x80004003
00653F93: call    0xa5fde4
00653F98: mov     ecx, dword ptr [edi]
00653F9A: call    0x437476
00653F9F: add     eax, 0x258
00653FA4: push    3
00653FA6: push    eax
00653FA7: lea     ecx, [ebp - 0x34]
00653FAA: call    0x402fab
00653FAF: mov     edi, dword ptr [ebp - 0x18]
00653FB2: mov     eax, dword ptr [ebp - 0x14]
00653FB5: add     edi, dword ptr [eax + 0x214]
00653FBB: mov     byte ptr [ebp - 4], 0x14
00653FBF: cmp     dword ptr [edi], esi
00653FC1: jne     0x653fcd
00653FC3: push    0x80004003
00653FC8: call    0xa5fde4
00653FCD: mov     ecx, dword ptr [edi]
00653FCF: lea     eax, [ebp - 0x1c]
00653FD2: push    eax
00653FD3: call    0x439dcb
00653FD8: mov     edi, eax
00653FDA: cmp     dword ptr [edi], esi
00653FDC: mov     byte ptr [ebp - 4], 0x15
```

## Candidate near `0x00653FB5`
```asm
00653F75: call    0x402f85
00653F7A: mov     edi, dword ptr [ebp - 0x18]
00653F7D: mov     eax, dword ptr [ebp - 0x14]
00653F80: add     edi, dword ptr [eax + 0x214]
00653F86: mov     byte ptr [ebp - 4], 0x13
00653F8A: cmp     dword ptr [edi], esi
00653F8C: jne     0x653f98
00653F8E: push    0x80004003
00653F93: call    0xa5fde4
00653F98: mov     ecx, dword ptr [edi]
00653F9A: call    0x437476
00653F9F: add     eax, 0x258
00653FA4: push    3
00653FA6: push    eax
00653FA7: lea     ecx, [ebp - 0x34]
00653FAA: call    0x402fab
00653FAF: mov     edi, dword ptr [ebp - 0x18]
00653FB2: mov     eax, dword ptr [ebp - 0x14]
00653FB5: add     edi, dword ptr [eax + 0x214]
00653FBB: mov     byte ptr [ebp - 4], 0x14
00653FBF: cmp     dword ptr [edi], esi
00653FC1: jne     0x653fcd
00653FC3: push    0x80004003
00653FC8: call    0xa5fde4
00653FCD: mov     ecx, dword ptr [edi]
00653FCF: lea     eax, [ebp - 0x1c]
00653FD2: push    eax
00653FD3: call    0x439dcb
00653FD8: mov     edi, eax
00653FDA: cmp     dword ptr [edi], esi
00653FDC: mov     byte ptr [ebp - 4], 0x15
00653FE0: jne     0x653fec
00653FE2: push    0x80004003
00653FE7: call    0xa5fde4
00653FEC: mov     eax, dword ptr [edi]
00653FEE: sub     esp, 0x10
00653FF1: mov     edi, esp
00653FF3: lea     esi, [ebp - 0x58]
00653FF6: movsd   dword ptr es:[edi], dword ptr [esi]
00653FF7: movsd   dword ptr es:[edi], dword ptr [esi]
00653FF8: mov     ecx, dword ptr [eax]
00653FFA: movsd   dword ptr es:[edi], dword ptr [esi]
00653FFB: movsd   dword ptr es:[edi], dword ptr [esi]
00653FFC: sub     esp, 0x10
00653FFF: mov     edi, esp
00654001: lea     esi, [ebp - 0x34]
```

## Candidate near `0x0065406F`
```asm
0065403F: pop     ecx
00654040: jge     0x654048
00654042: push    eax
00654043: call    0xa5fde4
00654048: and     byte ptr [ebp - 4], 0
0065404C: lea     eax, [ebp - 0x58]
0065404F: push    eax
00654050: call    0x40291d
00654055: test    eax, eax
00654057: pop     ecx
00654058: jge     0x654060
0065405A: push    eax
0065405B: call    0xa5fde4
00654060: push    ebx
00654061: lea     ecx, [ebp - 0x58]
00654064: call    0x402f85
00654069: mov     esi, dword ptr [ebp - 0x18]
0065406C: mov     edi, dword ptr [ebp - 0x14]
0065406F: add     esi, dword ptr [edi + 0x214]
00654075: mov     byte ptr [ebp - 4], 0x16
00654079: cmp     dword ptr [esi], 0
0065407C: jne     0x654088
0065407E: push    0x80004003
00654083: call    0xa5fde4
00654088: mov     ecx, dword ptr [esi]
0065408A: call    0x437476
0065408F: add     eax, 0x258
00654094: push    3
00654096: push    eax
00654097: lea     ecx, [ebp - 0x34]
0065409A: call    0x402fab
0065409F: mov     esi, dword ptr [ebp - 0x18]
006540A2: add     esi, dword ptr [edi + 0x214]
006540A8: mov     byte ptr [ebp - 4], 0x17
006540AC: cmp     dword ptr [esi], 0
006540AF: jne     0x6540bb
006540B1: push    0x80004003
006540B6: call    0xa5fde4
006540BB: mov     eax, dword ptr [esi]
006540BD: mov     esi, dword ptr [edi + 0x818]
006540C3: mov     dword ptr [ebp - 0x10], eax
006540C6: mov     eax, dword ptr [ebp + 8]
006540C9: cdq     
006540CA: idiv    esi
006540CC: sub     esp, 0x10
006540CF: mov     ecx, eax
```

## Candidate near `0x006540A2`
```asm
00654061: lea     ecx, [ebp - 0x58]
00654064: call    0x402f85
00654069: mov     esi, dword ptr [ebp - 0x18]
0065406C: mov     edi, dword ptr [ebp - 0x14]
0065406F: add     esi, dword ptr [edi + 0x214]
00654075: mov     byte ptr [ebp - 4], 0x16
00654079: cmp     dword ptr [esi], 0
0065407C: jne     0x654088
0065407E: push    0x80004003
00654083: call    0xa5fde4
00654088: mov     ecx, dword ptr [esi]
0065408A: call    0x437476
0065408F: add     eax, 0x258
00654094: push    3
00654096: push    eax
00654097: lea     ecx, [ebp - 0x34]
0065409A: call    0x402fab
0065409F: mov     esi, dword ptr [ebp - 0x18]
006540A2: add     esi, dword ptr [edi + 0x214]
006540A8: mov     byte ptr [ebp - 4], 0x17
006540AC: cmp     dword ptr [esi], 0
006540AF: jne     0x6540bb
006540B1: push    0x80004003
006540B6: call    0xa5fde4
006540BB: mov     eax, dword ptr [esi]
006540BD: mov     esi, dword ptr [edi + 0x818]
006540C3: mov     dword ptr [ebp - 0x10], eax
006540C6: mov     eax, dword ptr [ebp + 8]
006540C9: cdq     
006540CA: idiv    esi
006540CC: sub     esp, 0x10
006540CF: mov     ecx, eax
006540D1: mov     eax, dword ptr [ebp + 8]
006540D4: imul    ecx, ecx, 0x43
006540D7: add     ecx, dword ptr [edi + 0x820]
006540DD: cdq     
006540DE: idiv    esi
006540E0: mov     eax, dword ptr [edi + 0x81c]
006540E6: mov     edi, esp
006540E8: lea     esi, [ebp - 0x58]
006540EB: movsd   dword ptr es:[edi], dword ptr [esi]
006540EC: movsd   dword ptr es:[edi], dword ptr [esi]
006540ED: movsd   dword ptr es:[edi], dword ptr [esi]
006540EE: movsd   dword ptr es:[edi], dword ptr [esi]
006540EF: sub     esp, 0x10
006540F2: mov     edi, esp
```

## Candidate near `0x00654187`
```asm
00654157: push    eax
00654158: call    dword ptr [0xaf0268]
0065415E: lea     eax, [ebp - 0x44]
00654161: push    ebx
00654162: push    eax
00654163: call    0x402b8c
00654168: test    eax, eax
0065416A: pop     ecx
0065416B: pop     ecx
0065416C: jge     0x654174
0065416E: push    eax
0065416F: call    0xa5fde4
00654174: push    ebx
00654175: lea     ecx, [ebp - 0x34]
00654178: mov     byte ptr [ebp - 4], 0x18
0065417C: call    0x402f85
00654181: mov     esi, dword ptr [ebp - 0x18]
00654184: mov     eax, dword ptr [ebp - 0x14]
00654187: add     esi, dword ptr [eax + 0x214]
0065418D: mov     byte ptr [ebp - 4], 0x19
00654191: cmp     dword ptr [esi], 0
00654194: jne     0x6541a0
00654196: push    0x80004003
0065419B: call    0xa5fde4
006541A0: mov     ebx, dword ptr [esi]
006541A2: sub     esp, 0x10
006541A5: mov     edi, esp
006541A7: lea     esi, [ebp - 0x44]
006541AA: movsd   dword ptr es:[edi], dword ptr [esi]
006541AB: movsd   dword ptr es:[edi], dword ptr [esi]
006541AC: mov     eax, dword ptr [ebx]
006541AE: movsd   dword ptr es:[edi], dword ptr [esi]
006541AF: movsd   dword ptr es:[edi], dword ptr [esi]
006541B0: sub     esp, 0x10
006541B3: mov     edi, esp
006541B5: lea     esi, [ebp - 0x34]
006541B8: movsd   dword ptr es:[edi], dword ptr [esi]
006541B9: movsd   dword ptr es:[edi], dword ptr [esi]
006541BA: movsd   dword ptr es:[edi], dword ptr [esi]
006541BB: push    0
006541BD: push    ebx
006541BE: movsd   dword ptr es:[edi], dword ptr [esi]
006541BF: call    dword ptr [eax + 0x110]
006541C5: test    eax, eax
006541C7: jge     0x6541d5
006541C9: push    0xbd8358
```

## Candidate near `0x006542B8`
```asm
0065427C: mov     eax, 0xaa013f
00654281: call    0xa60b98
00654286: sub     esp, 0x88
0065428C: mov     eax, dword ptr [ebp + 8]
0065428F: push    ebx
00654290: push    esi
00654291: push    edi
00654292: xor     esi, esi
00654294: cmp     eax, esi
00654296: mov     edi, ecx
00654298: mov     dword ptr [ebp - 0x24], edi
0065429B: jl      0x654859
006542A1: cmp     eax, dword ptr [edi + 0x780]
006542A7: jge     0x654859
006542AD: mov     dword ptr [ebp - 0x1c], esi
006542B0: mov     ecx, eax
006542B2: shl     ecx, 2
006542B5: mov     dword ptr [ebp - 0x18], ecx
006542B8: add     ecx, dword ptr [edi + 0x214]
006542BE: push    esi
006542BF: mov     dword ptr [ebp - 4], esi
006542C2: call    0x428712
006542C7: mov     ebx, 0xbf6300
006542CC: push    ebx
006542CD: lea     ecx, [ebp - 0x34]
006542D0: call    0x402f85
006542D5: push    3
006542D7: push    esi
006542D8: lea     ecx, [ebp - 0x64]
006542DB: mov     byte ptr [ebp - 4], 1
006542DF: call    0x402fab
006542E4: cmp     dword ptr [0xbf14ec], esi
006542EA: mov     byte ptr [ebp - 4], 2
006542EE: jne     0x6542fa
006542F0: push    0x80004003
006542F5: call    0xa5fde4
006542FA: mov     ecx, dword ptr [0xbf14ec]
00654300: lea     eax, [ebp - 0x34]
00654303: push    eax
00654304: lea     eax, [ebp - 0x64]
00654307: push    eax
00654308: push    4
0065430A: push    esi
0065430B: push    esi
0065430C: push    esi
0065430D: push    esi
```

## Candidate near `0x0065431A`
```asm
006542EA: mov     byte ptr [ebp - 4], 2
006542EE: jne     0x6542fa
006542F0: push    0x80004003
006542F5: call    0xa5fde4
006542FA: mov     ecx, dword ptr [0xbf14ec]
00654300: lea     eax, [ebp - 0x34]
00654303: push    eax
00654304: lea     eax, [ebp - 0x64]
00654307: push    eax
00654308: push    4
0065430A: push    esi
0065430B: push    esi
0065430C: push    esi
0065430D: push    esi
0065430E: lea     eax, [ebp - 0x14]
00654311: push    eax
00654312: call    0x426c7e
00654317: mov     ecx, dword ptr [ebp - 0x18]
0065431A: add     ecx, dword ptr [edi + 0x214]
00654320: push    dword ptr [eax]
00654322: call    0x428712
00654327: lea     ecx, [ebp - 0x14]
0065432A: call    0x4156c5
0065432F: lea     eax, [ebp - 0x64]
00654332: push    eax
00654333: mov     byte ptr [ebp - 4], 1
00654337: call    0x40291d
0065433C: cmp     eax, esi
0065433E: pop     ecx
0065433F: jge     0x654347
00654341: push    eax
00654342: call    0xa5fde4
00654347: and     byte ptr [ebp - 4], 0
0065434B: lea     eax, [ebp - 0x34]
0065434E: push    eax
0065434F: call    0x40291d
00654354: cmp     eax, esi
00654356: pop     ecx
00654357: jge     0x65435f
00654359: push    eax
0065435A: call    0xa5fde4
0065435F: lea     eax, [ebp - 0x10]
00654362: push    eax
00654363: mov     ecx, edi
00654365: call    0x426604
0065436A: mov     eax, dword ptr [eax]
```

## Candidate near `0x0065437A`
```asm
0065434B: lea     eax, [ebp - 0x34]
0065434E: push    eax
0065434F: call    0x40291d
00654354: cmp     eax, esi
00654356: pop     ecx
00654357: jge     0x65435f
00654359: push    eax
0065435A: call    0xa5fde4
0065435F: lea     eax, [ebp - 0x10]
00654362: push    eax
00654363: mov     ecx, edi
00654365: call    0x426604
0065436A: mov     eax, dword ptr [eax]
0065436C: push    1
0065436E: push    eax
0065436F: lea     ecx, [ebp - 0x34]
00654372: call    0x410fdf
00654377: mov     esi, dword ptr [ebp - 0x18]
0065437A: add     esi, dword ptr [edi + 0x214]
00654380: mov     byte ptr [ebp - 4], 4
00654384: cmp     dword ptr [esi], 0
00654387: jne     0x654393
00654389: push    0x80004003
0065438E: call    0xa5fde4
00654393: mov     eax, dword ptr [esi]
00654395: mov     ecx, dword ptr [eax]
00654397: sub     esp, 0x10
0065439A: mov     edi, esp
0065439C: lea     esi, [ebp - 0x34]
0065439F: movsd   dword ptr es:[edi], dword ptr [esi]
006543A0: movsd   dword ptr es:[edi], dword ptr [esi]
006543A1: movsd   dword ptr es:[edi], dword ptr [esi]
006543A2: push    eax
006543A3: mov     dword ptr [ebp - 0x14], eax
006543A6: movsd   dword ptr es:[edi], dword ptr [esi]
006543A7: call    dword ptr [ecx + 0x64]
006543AA: test    eax, eax
006543AC: jge     0x6543bc
006543AE: push    0xbd8348
006543B3: push    dword ptr [ebp - 0x14]
006543B6: push    eax
006543B7: call    0xa5fdf2
006543BC: lea     eax, [ebp - 0x34]
006543BF: push    eax
006543C0: mov     byte ptr [ebp - 4], 3
006543C4: call    0x40291d
```

## Candidate near `0x006543FE`
```asm
006543CB: pop     ecx
006543CC: jge     0x6543d4
006543CE: push    eax
006543CF: call    0xa5fde4
006543D4: and     byte ptr [ebp - 4], 0
006543D8: lea     ecx, [ebp - 0x10]
006543DB: call    0x4156c5
006543E0: mov     edi, dword ptr [ebp - 0x24]
006543E3: lea     eax, [ebp - 0x14]
006543E6: push    eax
006543E7: mov     ecx, edi
006543E9: call    0x426604
006543EE: mov     eax, dword ptr [eax]
006543F0: push    1
006543F2: push    eax
006543F3: lea     ecx, [ebp - 0x34]
006543F6: call    0x410fdf
006543FB: mov     esi, dword ptr [ebp - 0x18]
006543FE: add     esi, dword ptr [edi + 0x214]
00654404: mov     byte ptr [ebp - 4], 6
00654408: cmp     dword ptr [esi], 0
0065440B: jne     0x654417
0065440D: push    0x80004003
00654412: call    0xa5fde4
00654417: mov     eax, dword ptr [esi]
00654419: mov     ecx, dword ptr [eax]
0065441B: sub     esp, 0x10
0065441E: mov     edi, esp
00654420: lea     esi, [ebp - 0x34]
00654423: movsd   dword ptr es:[edi], dword ptr [esi]
00654424: movsd   dword ptr es:[edi], dword ptr [esi]
00654425: movsd   dword ptr es:[edi], dword ptr [esi]
00654426: push    eax
00654427: mov     dword ptr [ebp - 0x10], eax
0065442A: movsd   dword ptr es:[edi], dword ptr [esi]
0065442B: call    dword ptr [ecx + 0xfc]
00654431: test    eax, eax
00654433: jge     0x654443
00654435: push    0xbd8358
0065443A: push    dword ptr [ebp - 0x10]
0065443D: push    eax
0065443E: call    0xa5fdf2
00654443: lea     eax, [ebp - 0x34]
00654446: push    eax
00654447: mov     byte ptr [ebp - 4], 5
0065444B: call    0x40291d
```

## Candidate near `0x0065446D`
```asm
00654435: push    0xbd8358
0065443A: push    dword ptr [ebp - 0x10]
0065443D: push    eax
0065443E: call    0xa5fdf2
00654443: lea     eax, [ebp - 0x34]
00654446: push    eax
00654447: mov     byte ptr [ebp - 4], 5
0065444B: call    0x40291d
00654450: test    eax, eax
00654452: pop     ecx
00654453: jge     0x65445b
00654455: push    eax
00654456: call    0xa5fde4
0065445B: and     byte ptr [ebp - 4], 0
0065445F: lea     ecx, [ebp - 0x14]
00654462: call    0x4156c5
00654467: mov     esi, dword ptr [ebp - 0x18]
0065446A: mov     edi, dword ptr [ebp - 0x24]
0065446D: add     esi, dword ptr [edi + 0x214]
00654473: cmp     dword ptr [esi], 0
00654476: jne     0x654482
00654478: push    0x80004003
0065447D: call    0xa5fde4
00654482: mov     esi, dword ptr [esi]
00654484: mov     eax, dword ptr [esi]
00654486: push    -1
00654488: push    esi
00654489: mov     dword ptr [ebp - 0x10], esi
0065448C: call    dword ptr [eax + 0xe0]
00654492: xor     esi, esi
00654494: cmp     eax, esi
00654496: jge     0x6544a6
00654498: push    0xbd8358
0065449D: push    dword ptr [ebp - 0x10]
006544A0: push    eax
006544A1: call    0xa5fdf2
006544A6: lea     eax, [ebp - 0x10]
006544A9: push    0x158b
006544AE: push    eax
006544AF: call    0x79e805
006544B4: mov     ecx, eax
006544B6: call    0x406455
006544BB: mov     ecx, dword ptr [edi + 0x210]
006544C1: mov     edx, dword ptr [ebp - 0x18]
006544C4: push    dword ptr [ecx + edx]
006544C7: mov     eax, dword ptr [eax]
```

## Candidate near `0x006545C0`
```asm
0065458B: mov     ecx, eax
0065458D: mov     byte ptr [ebp - 4], 0xe
00654591: call    0x4032b2
00654596: cmp     eax, esi
00654598: mov     dword ptr [ebp - 0x10], eax
0065459B: mov     dword ptr [ebp - 0x14], esi
0065459E: je      0x6545bd
006545A0: lea     eax, [ebp - 0x10]
006545A3: push    eax
006545A4: lea     ecx, [ebp - 0x14]
006545A7: call    0x41e527
006545AC: cmp     eax, esi
006545AE: jge     0x6545bd
006545B0: cmp     eax, 0x80004002
006545B5: je      0x6545bd
006545B7: push    eax
006545B8: call    0xa5fde4
006545BD: mov     esi, dword ptr [ebp - 0x18]
006545C0: add     esi, dword ptr [edi + 0x214]
006545C6: mov     eax, dword ptr [ebp - 0x14]
006545C9: cmp     dword ptr [esi], 0
006545CC: mov     byte ptr [ebp - 4], 0xf
006545D0: mov     dword ptr [ebp - 0x20], eax
006545D3: jne     0x6545df
006545D5: push    0x80004003
006545DA: call    0xa5fde4
006545DF: mov     esi, dword ptr [esi]
006545E1: lea     eax, [ebp - 0x44]
006545E4: push    eax
006545E5: lea     eax, [ebp - 0x54]
006545E8: push    eax
006545E9: lea     eax, [ebp - 0x74]
006545EC: push    eax
006545ED: lea     eax, [ebp - 0x64]
006545F0: push    eax
006545F1: lea     eax, [ebp - 0x34]
006545F4: push    eax
006545F5: push    dword ptr [ebp - 0x20]
006545F8: lea     eax, [ebp - 0x84]
006545FE: push    eax
006545FF: mov     ecx, esi
00654601: call    0x426bab
00654606: lea     eax, [ebp - 0x84]
0065460C: push    eax
0065460D: call    0x40291d
00654612: test    eax, eax
```

## Candidate near `0x006546D1`
```asm
0065469B: call    0xa5fde4
006546A0: and     byte ptr [ebp - 4], 0
006546A4: lea     eax, [ebp - 0x44]
006546A7: push    eax
006546A8: call    0x40291d
006546AD: test    eax, eax
006546AF: pop     ecx
006546B0: jge     0x6546b8
006546B2: push    eax
006546B3: call    0xa5fde4
006546B8: push    ebx
006546B9: lea     ecx, [ebp - 0x54]
006546BC: call    0x402f85
006546C1: push    ebx
006546C2: lea     ecx, [ebp - 0x44]
006546C5: mov     byte ptr [ebp - 4], 0x10
006546C9: call    0x402f85
006546CE: mov     esi, dword ptr [ebp - 0x18]
006546D1: add     esi, dword ptr [edi + 0x214]
006546D7: mov     byte ptr [ebp - 4], 0x11
006546DB: cmp     dword ptr [esi], 0
006546DE: jne     0x6546ea
006546E0: push    0x80004003
006546E5: call    0xa5fde4
006546EA: mov     esi, dword ptr [esi]
006546EC: lea     eax, [ebp - 0x10]
006546EF: push    eax
006546F0: mov     ecx, esi
006546F2: call    0x439dcb
006546F7: mov     esi, eax
006546F9: cmp     dword ptr [esi], 0
006546FC: mov     byte ptr [ebp - 4], 0x12
00654700: jne     0x65470c
00654702: push    0x80004003
00654707: call    0xa5fde4
0065470C: mov     eax, dword ptr [esi]
0065470E: sub     esp, 0x10
00654711: mov     edi, esp
00654713: lea     esi, [ebp - 0x54]
00654716: movsd   dword ptr es:[edi], dword ptr [esi]
00654717: movsd   dword ptr es:[edi], dword ptr [esi]
00654718: mov     ecx, dword ptr [eax]
0065471A: movsd   dword ptr es:[edi], dword ptr [esi]
0065471B: movsd   dword ptr es:[edi], dword ptr [esi]
0065471C: sub     esp, 0x10
0065471F: mov     edi, esp
```

## Candidate near `0x0065479C`
```asm
00654768: and     byte ptr [ebp - 4], 0
0065476C: lea     eax, [ebp - 0x54]
0065476F: push    eax
00654770: call    0x40291d
00654775: test    eax, eax
00654777: pop     ecx
00654778: jge     0x654780
0065477A: push    eax
0065477B: call    0xa5fde4
00654780: push    ebx
00654781: lea     ecx, [ebp - 0x54]
00654784: call    0x402f85
00654789: push    ebx
0065478A: lea     ecx, [ebp - 0x44]
0065478D: mov     byte ptr [ebp - 4], 0x13
00654791: call    0x402f85
00654796: mov     edi, dword ptr [ebp - 0x18]
00654799: mov     esi, dword ptr [ebp - 0x24]
0065479C: add     edi, dword ptr [esi + 0x214]
006547A2: mov     byte ptr [ebp - 4], 0x14
006547A6: cmp     dword ptr [edi], 0
006547A9: jne     0x6547b5
006547AB: push    0x80004003
006547B0: call    0xa5fde4
006547B5: mov     ebx, dword ptr [edi]
006547B7: mov     edi, dword ptr [esi + 0x818]
006547BD: mov     eax, dword ptr [ebp + 8]
006547C0: cdq     
006547C1: idiv    edi
006547C3: sub     esp, 0x10
006547C6: mov     ecx, eax
006547C8: mov     eax, dword ptr [ebp + 8]
006547CB: imul    ecx, ecx, 0x43
006547CE: add     ecx, dword ptr [esi + 0x820]
006547D4: cdq     
006547D5: idiv    edi
006547D7: mov     eax, dword ptr [esi + 0x81c]
006547DD: mov     edi, esp
006547DF: lea     esi, [ebp - 0x54]
006547E2: movsd   dword ptr es:[edi], dword ptr [esi]
006547E3: movsd   dword ptr es:[edi], dword ptr [esi]
006547E4: movsd   dword ptr es:[edi], dword ptr [esi]
006547E5: movsd   dword ptr es:[edi], dword ptr [esi]
006547E6: sub     esp, 0x10
006547E9: mov     edi, esp
006547EB: lea     esi, [ebp - 0x44]
```

## Candidate near `0x006548F9`
```asm
006548C4: push    dword ptr [ecx + esi]
006548C7: mov     byte ptr [ebp - 4], 1
006548CB: push    eax
006548CC: lea     eax, [ebp - 0x14]
006548CF: push    eax
006548D0: mov     dword ptr [ebp - 0x10], esi
006548D3: call    0x445b4b
006548D8: mov     eax, dword ptr [ebp - 0x18]
006548DB: and     byte ptr [ebp - 4], 0
006548DF: add     esp, 0xc
006548E2: cmp     eax, edi
006548E4: je      0x6548f0
006548E6: add     eax, -0xc
006548E9: push    eax
006548EA: call    0x428d13
006548EF: pop     ecx
006548F0: cmp     dword ptr [ebp + 0xc], edi
006548F3: je      0x654efa
006548F9: mov     ecx, dword ptr [ebx + 0x214]
006548FF: add     ecx, esi
00654901: push    edi
00654902: call    0x428712
00654907: push    0xbf6300
0065490C: lea     ecx, [ebp - 0x3c]
0065490F: call    0x402f85
00654914: push    3
00654916: push    edi
00654917: lea     ecx, [ebp - 0x2c]
0065491A: mov     byte ptr [ebp - 4], 2
0065491E: call    0x402fab
00654923: cmp     dword ptr [0xbf14ec], edi
00654929: mov     byte ptr [ebp - 4], 3
0065492D: jne     0x654939
0065492F: push    0x80004003
00654934: call    0xa5fde4
00654939: mov     ecx, dword ptr [0xbf14ec]
0065493F: lea     eax, [ebp - 0x3c]
00654942: push    eax
00654943: lea     eax, [ebp - 0x2c]
00654946: push    eax
00654947: push    4
00654949: push    edi
0065494A: push    edi
0065494B: push    edi
0065494C: push    edi
0065494D: lea     eax, [ebp + 0xc]
```

## Candidate near `0x00654956`
```asm
00654923: cmp     dword ptr [0xbf14ec], edi
00654929: mov     byte ptr [ebp - 4], 3
0065492D: jne     0x654939
0065492F: push    0x80004003
00654934: call    0xa5fde4
00654939: mov     ecx, dword ptr [0xbf14ec]
0065493F: lea     eax, [ebp - 0x3c]
00654942: push    eax
00654943: lea     eax, [ebp - 0x2c]
00654946: push    eax
00654947: push    4
00654949: push    edi
0065494A: push    edi
0065494B: push    edi
0065494C: push    edi
0065494D: lea     eax, [ebp + 0xc]
00654950: push    eax
00654951: call    0x426c7e
00654956: mov     ecx, dword ptr [ebx + 0x214]
0065495C: push    dword ptr [eax]
0065495E: add     ecx, esi
00654960: call    0x428712
00654965: lea     ecx, [ebp + 0xc]
00654968: call    0x4156c5
0065496D: lea     eax, [ebp - 0x2c]
00654970: push    eax
00654971: mov     byte ptr [ebp - 4], 2
00654975: call    0x40291d
0065497A: cmp     eax, edi
0065497C: pop     ecx
0065497D: jge     0x654985
0065497F: push    eax
00654980: call    0xa5fde4
00654985: and     byte ptr [ebp - 4], 0
00654989: lea     eax, [ebp - 0x3c]
0065498C: push    eax
0065498D: call    0x40291d
00654992: cmp     eax, edi
00654994: pop     ecx
00654995: jge     0x65499d
00654997: push    eax
00654998: call    0xa5fde4
0065499D: lea     eax, [ebp - 0x18]
006549A0: push    eax
006549A1: mov     ecx, ebx
006549A3: call    0x426604
```

## Candidate near `0x006549B5`
```asm
00654985: and     byte ptr [ebp - 4], 0
00654989: lea     eax, [ebp - 0x3c]
0065498C: push    eax
0065498D: call    0x40291d
00654992: cmp     eax, edi
00654994: pop     ecx
00654995: jge     0x65499d
00654997: push    eax
00654998: call    0xa5fde4
0065499D: lea     eax, [ebp - 0x18]
006549A0: push    eax
006549A1: mov     ecx, ebx
006549A3: call    0x426604
006549A8: mov     eax, dword ptr [eax]
006549AA: push    1
006549AC: push    eax
006549AD: lea     ecx, [ebp - 0x3c]
006549B0: call    0x410fdf
006549B5: mov     esi, dword ptr [ebx + 0x214]
006549BB: add     esi, dword ptr [ebp - 0x10]
006549BE: mov     byte ptr [ebp - 4], 5
006549C2: cmp     dword ptr [esi], edi
006549C4: jne     0x6549d0
006549C6: push    0x80004003
006549CB: call    0xa5fde4
006549D0: mov     eax, dword ptr [esi]
006549D2: mov     ecx, dword ptr [eax]
006549D4: sub     esp, 0x10
006549D7: mov     edi, esp
006549D9: lea     esi, [ebp - 0x3c]
006549DC: movsd   dword ptr es:[edi], dword ptr [esi]
006549DD: movsd   dword ptr es:[edi], dword ptr [esi]
006549DE: movsd   dword ptr es:[edi], dword ptr [esi]
006549DF: push    eax
006549E0: mov     dword ptr [ebp + 0xc], eax
006549E3: movsd   dword ptr es:[edi], dword ptr [esi]
006549E4: call    dword ptr [ecx + 0x64]
006549E7: test    eax, eax
006549E9: jge     0x6549f9
006549EB: push    0xbd8348
006549F0: push    dword ptr [ebp + 0xc]
006549F3: push    eax
006549F4: call    0xa5fdf2
006549F9: lea     eax, [ebp - 0x3c]
006549FC: push    eax
006549FD: mov     byte ptr [ebp - 4], 4
```

## Candidate near `0x00654A35`
```asm
00654A01: call    0x40291d
00654A06: test    eax, eax
00654A08: pop     ecx
00654A09: jge     0x654a11
00654A0B: push    eax
00654A0C: call    0xa5fde4
00654A11: and     byte ptr [ebp - 4], 0
00654A15: lea     ecx, [ebp - 0x18]
00654A18: call    0x4156c5
00654A1D: lea     eax, [ebp - 0x18]
00654A20: push    eax
00654A21: mov     ecx, ebx
00654A23: call    0x426604
00654A28: mov     eax, dword ptr [eax]
00654A2A: push    1
00654A2C: push    eax
00654A2D: lea     ecx, [ebp - 0x3c]
00654A30: call    0x410fdf
00654A35: mov     esi, dword ptr [ebx + 0x214]
00654A3B: add     esi, dword ptr [ebp - 0x10]
00654A3E: mov     byte ptr [ebp - 4], 7
00654A42: cmp     dword ptr [esi], 0
00654A45: jne     0x654a51
00654A47: push    0x80004003
00654A4C: call    0xa5fde4
00654A51: mov     eax, dword ptr [esi]
00654A53: mov     ecx, dword ptr [eax]
00654A55: sub     esp, 0x10
00654A58: mov     edi, esp
00654A5A: lea     esi, [ebp - 0x3c]
00654A5D: movsd   dword ptr es:[edi], dword ptr [esi]
00654A5E: movsd   dword ptr es:[edi], dword ptr [esi]
00654A5F: movsd   dword ptr es:[edi], dword ptr [esi]
00654A60: push    eax
00654A61: mov     dword ptr [ebp + 0xc], eax
00654A64: movsd   dword ptr es:[edi], dword ptr [esi]
00654A65: call    dword ptr [ecx + 0xfc]
00654A6B: test    eax, eax
00654A6D: jge     0x654a7d
00654A6F: push    0xbd8358
00654A74: push    dword ptr [ebp + 0xc]
00654A77: push    eax
00654A78: call    0xa5fdf2
00654A7D: lea     eax, [ebp - 0x3c]
00654A80: push    eax
00654A81: mov     byte ptr [ebp - 4], 6
```

## Candidate near `0x00654AA1`
```asm
00654A6B: test    eax, eax
00654A6D: jge     0x654a7d
00654A6F: push    0xbd8358
00654A74: push    dword ptr [ebp + 0xc]
00654A77: push    eax
00654A78: call    0xa5fdf2
00654A7D: lea     eax, [ebp - 0x3c]
00654A80: push    eax
00654A81: mov     byte ptr [ebp - 4], 6
00654A85: call    0x40291d
00654A8A: test    eax, eax
00654A8C: pop     ecx
00654A8D: jge     0x654a95
00654A8F: push    eax
00654A90: call    0xa5fde4
00654A95: and     byte ptr [ebp - 4], 0
00654A99: lea     ecx, [ebp - 0x18]
00654A9C: call    0x4156c5
00654AA1: mov     esi, dword ptr [ebx + 0x214]
00654AA7: add     esi, dword ptr [ebp - 0x10]
00654AAA: cmp     dword ptr [esi], 0
00654AAD: jne     0x654ab9
00654AAF: push    0x80004003
00654AB4: call    0xa5fde4
00654AB9: mov     esi, dword ptr [esi]
00654ABB: mov     eax, dword ptr [esi]
00654ABD: push    -1
00654ABF: push    esi
00654AC0: call    dword ptr [eax + 0xe0]
00654AC6: test    eax, eax
00654AC8: jge     0x654ad6
00654ACA: push    0xbd8358
00654ACF: push    esi
00654AD0: push    eax
00654AD1: call    0xa5fdf2
00654AD6: mov     esi, 0xbf6300
00654ADB: push    esi
00654ADC: lea     ecx, [ebp - 0x2c]
00654ADF: call    0x402f85
00654AE4: push    esi
00654AE5: lea     ecx, [ebp - 0x3c]
00654AE8: mov     byte ptr [ebp - 4], 8
00654AEC: call    0x402f85
00654AF1: mov     esi, dword ptr [ebx + 0x214]
00654AF7: add     esi, dword ptr [ebp - 0x10]
00654AFA: mov     byte ptr [ebp - 4], 9
```

## Candidate near `0x00654AF1`
```asm
00654ABB: mov     eax, dword ptr [esi]
00654ABD: push    -1
00654ABF: push    esi
00654AC0: call    dword ptr [eax + 0xe0]
00654AC6: test    eax, eax
00654AC8: jge     0x654ad6
00654ACA: push    0xbd8358
00654ACF: push    esi
00654AD0: push    eax
00654AD1: call    0xa5fdf2
00654AD6: mov     esi, 0xbf6300
00654ADB: push    esi
00654ADC: lea     ecx, [ebp - 0x2c]
00654ADF: call    0x402f85
00654AE4: push    esi
00654AE5: lea     ecx, [ebp - 0x3c]
00654AE8: mov     byte ptr [ebp - 4], 8
00654AEC: call    0x402f85
00654AF1: mov     esi, dword ptr [ebx + 0x214]
00654AF7: add     esi, dword ptr [ebp - 0x10]
00654AFA: mov     byte ptr [ebp - 4], 9
00654AFE: cmp     dword ptr [esi], 0
00654B01: jne     0x654b0d
00654B03: push    0x80004003
00654B08: call    0xa5fde4
00654B0D: mov     edi, dword ptr [ebx + 0x818]
00654B13: mov     eax, dword ptr [ebp + 8]
00654B16: cdq     
00654B17: idiv    edi
00654B19: mov     esi, dword ptr [esi]
00654B1B: mov     dword ptr [ebp + 0xc], esi
00654B1E: sub     esp, 0x10
00654B21: mov     ecx, eax
00654B23: mov     eax, dword ptr [ebp + 8]
00654B26: imul    ecx, ecx, 0x43
00654B29: cdq     
00654B2A: idiv    edi
00654B2C: mov     eax, dword ptr [esi]
00654B2E: add     ecx, dword ptr [ebx + 0x820]
00654B34: mov     edi, esp
00654B36: lea     esi, [ebp - 0x2c]
00654B39: movsd   dword ptr es:[edi], dword ptr [esi]
00654B3A: movsd   dword ptr es:[edi], dword ptr [esi]
00654B3B: movsd   dword ptr es:[edi], dword ptr [esi]
00654B3C: movsd   dword ptr es:[edi], dword ptr [esi]
00654B3D: sub     esp, 0x10
```

## Candidate near `0x00654C7A`
```asm
00654C43: call    0x403935
00654C48: mov     ecx, eax
00654C4A: mov     byte ptr [ebp - 4], 0x10
00654C4E: call    0x4032b2
00654C53: cmp     eax, edi
00654C55: mov     dword ptr [ebp - 0x18], eax
00654C58: mov     dword ptr [ebp + 0xc], edi
00654C5B: je      0x654c7a
00654C5D: lea     eax, [ebp - 0x18]
00654C60: push    eax
00654C61: lea     ecx, [ebp + 0xc]
00654C64: call    0x41e527
00654C69: cmp     eax, edi
00654C6B: jge     0x654c7a
00654C6D: cmp     eax, 0x80004002
00654C72: je      0x654c7a
00654C74: push    eax
00654C75: call    0xa5fde4
00654C7A: mov     edi, dword ptr [ebx + 0x214]
00654C80: add     edi, dword ptr [ebp - 0x10]
00654C83: mov     eax, dword ptr [ebp + 0xc]
00654C86: cmp     dword ptr [edi], 0
00654C89: mov     byte ptr [ebp - 4], 0x11
00654C8D: mov     dword ptr [ebp - 0x1c], eax
00654C90: jne     0x654c9c
00654C92: push    0x80004003
00654C97: call    0xa5fde4
00654C9C: mov     ecx, dword ptr [edi]
00654C9E: lea     eax, [ebp - 0x6c]
00654CA1: push    eax
00654CA2: lea     eax, [ebp - 0x5c]
00654CA5: push    eax
00654CA6: lea     eax, [ebp - 0x4c]
00654CA9: push    eax
00654CAA: lea     eax, [ebp - 0x2c]
00654CAD: push    eax
00654CAE: lea     eax, [ebp - 0x3c]
00654CB1: push    eax
00654CB2: push    dword ptr [ebp - 0x1c]
00654CB5: lea     eax, [ebp - 0x7c]
00654CB8: push    eax
00654CB9: call    0x426bab
00654CBE: lea     eax, [ebp - 0x7c]
00654CC1: push    eax
00654CC2: call    0x40291d
00654CC7: test    eax, eax
```

## Candidate near `0x00654D83`
```asm
00654D4F: push    eax
00654D50: call    0xa5fde4
00654D55: and     byte ptr [ebp - 4], 0
00654D59: lea     eax, [ebp - 0x6c]
00654D5C: push    eax
00654D5D: call    0x40291d
00654D62: test    eax, eax
00654D64: pop     ecx
00654D65: jge     0x654d6d
00654D67: push    eax
00654D68: call    0xa5fde4
00654D6D: push    esi
00654D6E: lea     ecx, [ebp - 0x5c]
00654D71: call    0x402f85
00654D76: push    esi
00654D77: lea     ecx, [ebp - 0x6c]
00654D7A: mov     byte ptr [ebp - 4], 0x12
00654D7E: call    0x402f85
00654D83: mov     esi, dword ptr [ebx + 0x214]
00654D89: add     esi, dword ptr [ebp - 0x10]
00654D8C: mov     byte ptr [ebp - 4], 0x13
00654D90: cmp     dword ptr [esi], 0
00654D93: jne     0x654d9f
00654D95: push    0x80004003
00654D9A: call    0xa5fde4
00654D9F: mov     ecx, dword ptr [esi]
00654DA1: lea     eax, [ebp - 0x1c]
00654DA4: push    eax
00654DA5: call    0x439dcb
00654DAA: mov     esi, eax
00654DAC: cmp     dword ptr [esi], 0
00654DAF: mov     byte ptr [ebp - 4], 0x14
00654DB3: jne     0x654dbf
00654DB5: push    0x80004003
00654DBA: call    0xa5fde4
00654DBF: mov     eax, dword ptr [esi]
00654DC1: sub     esp, 0x10
00654DC4: mov     edi, esp
00654DC6: lea     esi, [ebp - 0x5c]
00654DC9: movsd   dword ptr es:[edi], dword ptr [esi]
00654DCA: movsd   dword ptr es:[edi], dword ptr [esi]
00654DCB: mov     ecx, dword ptr [eax]
00654DCD: movsd   dword ptr es:[edi], dword ptr [esi]
00654DCE: movsd   dword ptr es:[edi], dword ptr [esi]
00654DCF: sub     esp, 0x10
00654DD2: mov     edi, esp
```

## Candidate near `0x00654E4E`
```asm
00654E16: call    0xa5fde4
00654E1B: and     byte ptr [ebp - 4], 0
00654E1F: lea     eax, [ebp - 0x5c]
00654E22: push    eax
00654E23: call    0x40291d
00654E28: test    eax, eax
00654E2A: pop     ecx
00654E2B: jge     0x654e33
00654E2D: push    eax
00654E2E: call    0xa5fde4
00654E33: mov     esi, 0xbf6300
00654E38: push    esi
00654E39: lea     ecx, [ebp - 0x5c]
00654E3C: call    0x402f85
00654E41: push    esi
00654E42: lea     ecx, [ebp - 0x6c]
00654E45: mov     byte ptr [ebp - 4], 0x15
00654E49: call    0x402f85
00654E4E: mov     esi, dword ptr [ebx + 0x214]
00654E54: add     esi, dword ptr [ebp - 0x10]
00654E57: mov     byte ptr [ebp - 4], 0x16
00654E5B: cmp     dword ptr [esi], 0
00654E5E: jne     0x654e6a
00654E60: push    0x80004003
00654E65: call    0xa5fde4
00654E6A: mov     edi, dword ptr [ebx + 0x818]
00654E70: mov     eax, dword ptr [ebp + 8]
00654E73: cdq     
00654E74: idiv    edi
00654E76: mov     esi, dword ptr [esi]
00654E78: mov     dword ptr [ebp + 0xc], esi
00654E7B: sub     esp, 0x10
00654E7E: mov     ecx, eax
00654E80: mov     eax, dword ptr [ebp + 8]
00654E83: imul    ecx, ecx, 0x43
00654E86: cdq     
00654E87: idiv    edi
00654E89: mov     eax, dword ptr [ebx + 0x81c]
00654E8F: add     ecx, dword ptr [ebx + 0x820]
00654E95: mov     edi, esp
00654E97: sub     esp, 0x10
00654E9A: imul    edx, edx, 0x38
00654E9D: lea     eax, [edx + eax + 0x31]
00654EA1: mov     edx, dword ptr [esi]
00654EA3: lea     esi, [ebp - 0x5c]
00654EA6: movsd   dword ptr es:[edi], dword ptr [esi]
```

## Candidate near `0x00654F06`
```asm
00654ED4: mov     byte ptr [ebp - 4], 0x15
00654ED8: call    0x40291d
00654EDD: test    eax, eax
00654EDF: pop     ecx
00654EE0: jge     0x654ee8
00654EE2: push    eax
00654EE3: call    0xa5fde4
00654EE8: and     byte ptr [ebp - 4], 0
00654EEC: lea     eax, [ebp - 0x5c]
00654EEF: push    eax
00654EF0: call    0x40291d
00654EF5: pop     ecx
00654EF6: test    eax, eax
00654EF8: jmp     0x654f48
00654EFA: push    3
00654EFC: push    1
00654EFE: lea     ecx, [ebp - 0x6c]
00654F01: call    0x402fab
00654F06: mov     esi, dword ptr [ebx + 0x214]
00654F0C: add     esi, dword ptr [ebp - 0x10]
00654F0F: mov     byte ptr [ebp - 4], 0x17
00654F13: cmp     dword ptr [esi], edi
00654F15: jne     0x654f21
00654F17: push    0x80004003
00654F1C: call    0xa5fde4
00654F21: mov     ecx, dword ptr [esi]
00654F23: lea     eax, [ebp - 0x6c]
00654F26: push    eax
00654F27: lea     eax, [ebp + 0xc]
00654F2A: push    eax
00654F2B: call    0x4143fb
00654F30: lea     ecx, [ebp + 0xc]
00654F33: call    0x4156ab
00654F38: and     byte ptr [ebp - 4], 0
00654F3C: lea     eax, [ebp - 0x6c]
00654F3F: push    eax
00654F40: call    0x40291d
00654F45: pop     ecx
00654F46: cmp     eax, edi
00654F48: jge     0x654f50
00654F4A: push    eax
00654F4B: call    0xa5fde4
00654F50: mov     esi, 0xbf6300
00654F55: push    esi
00654F56: lea     ecx, [ebp - 0x2c]
00654F59: call    0x402f85
```

## Candidate near `0x00655034`
```asm
00654FFC: call    0x403935
00655001: mov     ecx, eax
00655003: mov     byte ptr [ebp - 4], 0x1e
00655007: call    0x4032b2
0065500C: and     dword ptr [ebp + 0xc], 0
00655010: test    eax, eax
00655012: mov     dword ptr [ebp - 0x1c], eax
00655015: je      0x655034
00655017: lea     eax, [ebp - 0x1c]
0065501A: push    eax
0065501B: lea     ecx, [ebp + 0xc]
0065501E: call    0x41e527
00655023: test    eax, eax
00655025: jge     0x655034
00655027: cmp     eax, 0x80004002
0065502C: je      0x655034
0065502E: push    eax
0065502F: call    0xa5fde4
00655034: mov     edi, dword ptr [ebx + 0x214]
0065503A: add     edi, dword ptr [ebp - 0x10]
0065503D: mov     eax, dword ptr [ebp + 0xc]
00655040: cmp     dword ptr [edi], 0
00655043: mov     byte ptr [ebp - 4], 0x1f
00655047: mov     dword ptr [ebp - 0x18], eax
0065504A: jne     0x655056
0065504C: push    0x80004003
00655051: call    0xa5fde4
00655056: mov     ecx, dword ptr [edi]
00655058: lea     eax, [ebp - 0x2c]
0065505B: push    eax
0065505C: lea     eax, [ebp - 0x3c]
0065505F: push    eax
00655060: lea     eax, [ebp - 0x4c]
00655063: push    eax
00655064: lea     eax, [ebp - 0x5c]
00655067: push    eax
00655068: lea     eax, [ebp - 0x6c]
0065506B: push    eax
0065506C: push    dword ptr [ebp - 0x18]
0065506F: lea     eax, [ebp - 0x8c]
00655075: push    eax
00655076: call    0x426bab
0065507B: lea     eax, [ebp - 0x8c]
00655081: push    eax
00655082: call    0x40291d
00655087: test    eax, eax
```

## Candidate near `0x00655135`
```asm
00655104: call    0x40291d
00655109: cmp     eax, edi
0065510B: pop     ecx
0065510C: jge     0x655114
0065510E: push    eax
0065510F: call    0xa5fde4
00655114: and     byte ptr [ebp - 4], 0
00655118: lea     eax, [ebp - 0x2c]
0065511B: push    eax
0065511C: call    0x40291d
00655121: cmp     eax, edi
00655123: pop     ecx
00655124: jge     0x65512c
00655126: push    eax
00655127: call    0xa5fde4
0065512C: push    esi
0065512D: lea     ecx, [ebp - 0x5c]
00655130: call    0x402f85
00655135: mov     esi, dword ptr [ebx + 0x214]
0065513B: add     esi, dword ptr [ebp - 0x10]
0065513E: mov     byte ptr [ebp - 4], 0x20
00655142: cmp     dword ptr [esi], edi
00655144: jne     0x655150
00655146: push    0x80004003
0065514B: call    0xa5fde4
00655150: mov     ecx, dword ptr [esi]
00655152: call    0x437476
00655157: add     eax, 0x258
0065515C: push    3
0065515E: push    eax
0065515F: lea     ecx, [ebp - 0x6c]
00655162: call    0x402fab
00655167: mov     esi, dword ptr [ebx + 0x214]
0065516D: add     esi, dword ptr [ebp - 0x10]
00655170: mov     byte ptr [ebp - 4], 0x21
00655174: cmp     dword ptr [esi], edi
00655176: jne     0x655182
00655178: push    0x80004003
0065517D: call    0xa5fde4
00655182: mov     esi, dword ptr [esi]
00655184: lea     eax, [ebp - 0x1c]
00655187: push    eax
00655188: mov     ecx, esi
0065518A: call    0x439dcb
0065518F: mov     esi, eax
00655191: cmp     dword ptr [esi], edi
```

## Candidate near `0x00655167`
```asm
00655127: call    0xa5fde4
0065512C: push    esi
0065512D: lea     ecx, [ebp - 0x5c]
00655130: call    0x402f85
00655135: mov     esi, dword ptr [ebx + 0x214]
0065513B: add     esi, dword ptr [ebp - 0x10]
0065513E: mov     byte ptr [ebp - 4], 0x20
00655142: cmp     dword ptr [esi], edi
00655144: jne     0x655150
00655146: push    0x80004003
0065514B: call    0xa5fde4
00655150: mov     ecx, dword ptr [esi]
00655152: call    0x437476
00655157: add     eax, 0x258
0065515C: push    3
0065515E: push    eax
0065515F: lea     ecx, [ebp - 0x6c]
00655162: call    0x402fab
00655167: mov     esi, dword ptr [ebx + 0x214]
0065516D: add     esi, dword ptr [ebp - 0x10]
00655170: mov     byte ptr [ebp - 4], 0x21
00655174: cmp     dword ptr [esi], edi
00655176: jne     0x655182
00655178: push    0x80004003
0065517D: call    0xa5fde4
00655182: mov     esi, dword ptr [esi]
00655184: lea     eax, [ebp - 0x1c]
00655187: push    eax
00655188: mov     ecx, esi
0065518A: call    0x439dcb
0065518F: mov     esi, eax
00655191: cmp     dword ptr [esi], edi
00655193: mov     byte ptr [ebp - 4], 0x22
00655197: jne     0x6551a3
00655199: push    0x80004003
0065519E: call    0xa5fde4
006551A3: mov     eax, dword ptr [esi]
006551A5: sub     esp, 0x10
006551A8: mov     edi, esp
006551AA: lea     esi, [ebp - 0x5c]
006551AD: movsd   dword ptr es:[edi], dword ptr [esi]
006551AE: movsd   dword ptr es:[edi], dword ptr [esi]
006551AF: mov     ecx, dword ptr [eax]
006551B1: movsd   dword ptr es:[edi], dword ptr [esi]
006551B2: movsd   dword ptr es:[edi], dword ptr [esi]
006551B3: sub     esp, 0x10
```

## Candidate near `0x00655224`
```asm
006551EF: call    0x40291d
006551F4: test    eax, eax
006551F6: pop     ecx
006551F7: jge     0x6551ff
006551F9: push    eax
006551FA: call    0xa5fde4
006551FF: and     byte ptr [ebp - 4], 0
00655203: lea     eax, [ebp - 0x5c]
00655206: push    eax
00655207: call    0x40291d
0065520C: test    eax, eax
0065520E: pop     ecx
0065520F: jge     0x655217
00655211: push    eax
00655212: call    0xa5fde4
00655217: push    0xbf6300
0065521C: lea     ecx, [ebp - 0x5c]
0065521F: call    0x402f85
00655224: mov     esi, dword ptr [ebx + 0x214]
0065522A: add     esi, dword ptr [ebp - 0x10]
0065522D: mov     byte ptr [ebp - 4], 0x23
00655231: cmp     dword ptr [esi], 0
00655234: jne     0x655240
00655236: push    0x80004003
0065523B: call    0xa5fde4
00655240: mov     ecx, dword ptr [esi]
00655242: call    0x437476
00655247: add     eax, 0x258
0065524C: push    3
0065524E: push    eax
0065524F: lea     ecx, [ebp - 0x6c]
00655252: call    0x402fab
00655257: mov     esi, dword ptr [ebx + 0x214]
0065525D: add     esi, dword ptr [ebp - 0x10]
00655260: mov     byte ptr [ebp - 4], 0x24
00655264: cmp     dword ptr [esi], 0
00655267: jne     0x655273
00655269: push    0x80004003
0065526E: call    0xa5fde4
00655273: mov     edi, dword ptr [ebx + 0x818]
00655279: mov     eax, dword ptr [ebp + 8]
0065527C: cdq     
0065527D: idiv    edi
0065527F: mov     esi, dword ptr [esi]
00655281: mov     dword ptr [ebp + 0xc], esi
00655284: sub     esp, 0x10
```

## Candidate near `0x00655257`
```asm
00655212: call    0xa5fde4
00655217: push    0xbf6300
0065521C: lea     ecx, [ebp - 0x5c]
0065521F: call    0x402f85
00655224: mov     esi, dword ptr [ebx + 0x214]
0065522A: add     esi, dword ptr [ebp - 0x10]
0065522D: mov     byte ptr [ebp - 4], 0x23
00655231: cmp     dword ptr [esi], 0
00655234: jne     0x655240
00655236: push    0x80004003
0065523B: call    0xa5fde4
00655240: mov     ecx, dword ptr [esi]
00655242: call    0x437476
00655247: add     eax, 0x258
0065524C: push    3
0065524E: push    eax
0065524F: lea     ecx, [ebp - 0x6c]
00655252: call    0x402fab
00655257: mov     esi, dword ptr [ebx + 0x214]
0065525D: add     esi, dword ptr [ebp - 0x10]
00655260: mov     byte ptr [ebp - 4], 0x24
00655264: cmp     dword ptr [esi], 0
00655267: jne     0x655273
00655269: push    0x80004003
0065526E: call    0xa5fde4
00655273: mov     edi, dword ptr [ebx + 0x818]
00655279: mov     eax, dword ptr [ebp + 8]
0065527C: cdq     
0065527D: idiv    edi
0065527F: mov     esi, dword ptr [esi]
00655281: mov     dword ptr [ebp + 0xc], esi
00655284: sub     esp, 0x10
00655287: mov     ecx, eax
00655289: mov     eax, dword ptr [ebp + 8]
0065528C: imul    ecx, ecx, 0x43
0065528F: cdq     
00655290: idiv    edi
00655292: mov     eax, dword ptr [esi]
00655294: add     ecx, dword ptr [ebx + 0x820]
0065529A: mov     edi, esp
0065529C: lea     esi, [ebp - 0x5c]
0065529F: movsd   dword ptr es:[edi], dword ptr [esi]
006552A0: movsd   dword ptr es:[edi], dword ptr [esi]
006552A1: movsd   dword ptr es:[edi], dword ptr [esi]
006552A2: movsd   dword ptr es:[edi], dword ptr [esi]
006552A3: sub     esp, 0x10
```

## Candidate near `0x00655320`
```asm
006552E8: call    0xa5fde4
006552ED: and     byte ptr [ebp - 4], 0
006552F1: lea     eax, [ebp - 0x5c]
006552F4: push    eax
006552F5: call    0x40291d
006552FA: test    eax, eax
006552FC: pop     ecx
006552FD: jge     0x655305
006552FF: push    eax
00655300: call    0xa5fde4
00655305: mov     esi, 0xbf6300
0065530A: push    esi
0065530B: lea     ecx, [ebp - 0x5c]
0065530E: call    0x402f85
00655313: push    esi
00655314: lea     ecx, [ebp - 0x6c]
00655317: mov     byte ptr [ebp - 4], 0x25
0065531B: call    0x402f85
00655320: mov     ebx, dword ptr [ebx + 0x214]
00655326: add     ebx, dword ptr [ebp - 0x10]
00655329: mov     byte ptr [ebp - 4], 0x26
0065532D: cmp     dword ptr [ebx], 0
00655330: jne     0x65533c
00655332: push    0x80004003
00655337: call    0xa5fde4
0065533C: sub     esp, 0x10
0065533F: mov     edi, esp
00655341: mov     ebx, dword ptr [ebx]
00655343: lea     esi, [ebp - 0x5c]
00655346: movsd   dword ptr es:[edi], dword ptr [esi]
00655347: movsd   dword ptr es:[edi], dword ptr [esi]
00655348: mov     eax, dword ptr [ebx]
0065534A: movsd   dword ptr es:[edi], dword ptr [esi]
0065534B: movsd   dword ptr es:[edi], dword ptr [esi]
0065534C: sub     esp, 0x10
0065534F: mov     edi, esp
00655351: lea     esi, [ebp - 0x6c]
00655354: movsd   dword ptr es:[edi], dword ptr [esi]
00655355: movsd   dword ptr es:[edi], dword ptr [esi]
00655356: movsd   dword ptr es:[edi], dword ptr [esi]
00655357: push    0
00655359: push    ebx
0065535A: movsd   dword ptr es:[edi], dword ptr [esi]
0065535B: call    dword ptr [eax + 0x110]
00655361: test    eax, eax
00655363: jge     0x655371
```

## Candidate near `0x0065544F`
```asm
0065541E: shl     esi, 2
00655421: push    dword ptr [ecx + esi]
00655424: mov     byte ptr [ebp - 4], 1
00655428: push    eax
00655429: lea     eax, [ebp - 0x18]
0065542C: push    eax
0065542D: mov     dword ptr [ebp - 0x10], esi
00655430: call    0x445b4b
00655435: mov     eax, dword ptr [ebp - 0x14]
00655438: and     byte ptr [ebp - 4], 0
0065543C: add     esp, 0xc
0065543F: cmp     eax, edi
00655441: je      0x65544d
00655443: add     eax, -0xc
00655446: push    eax
00655447: call    0x428d13
0065544C: pop     ecx
0065544D: mov     ecx, esi
0065544F: add     ecx, dword ptr [ebx + 0x214]
00655455: push    edi
00655456: call    0x428712
0065545B: push    0xbf6300
00655460: lea     ecx, [ebp - 0x3c]
00655463: call    0x402f85
00655468: push    3
0065546A: push    edi
0065546B: lea     ecx, [ebp - 0x2c]
0065546E: mov     byte ptr [ebp - 4], 2
00655472: call    0x402fab
00655477: cmp     dword ptr [0xbf14ec], edi
0065547D: mov     byte ptr [ebp - 4], 3
00655481: jne     0x65548d
00655483: push    0x80004003
00655488: call    0xa5fde4
0065548D: mov     ecx, dword ptr [0xbf14ec]
00655493: lea     eax, [ebp - 0x3c]
00655496: push    eax
00655497: lea     eax, [ebp - 0x2c]
0065549A: push    eax
0065549B: push    4
0065549D: push    edi
0065549E: push    edi
0065549F: push    edi
006554A0: push    edi
006554A1: lea     eax, [ebp - 0x14]
006554A4: push    eax
```

## Candidate near `0x006554AE`
```asm
00655481: jne     0x65548d
00655483: push    0x80004003
00655488: call    0xa5fde4
0065548D: mov     ecx, dword ptr [0xbf14ec]
00655493: lea     eax, [ebp - 0x3c]
00655496: push    eax
00655497: lea     eax, [ebp - 0x2c]
0065549A: push    eax
0065549B: push    4
0065549D: push    edi
0065549E: push    edi
0065549F: push    edi
006554A0: push    edi
006554A1: lea     eax, [ebp - 0x14]
006554A4: push    eax
006554A5: call    0x426c7e
006554AA: push    dword ptr [eax]
006554AC: mov     ecx, esi
006554AE: add     ecx, dword ptr [ebx + 0x214]
006554B4: call    0x428712
006554B9: lea     ecx, [ebp - 0x14]
006554BC: call    0x4156c5
006554C1: lea     eax, [ebp - 0x2c]
006554C4: push    eax
006554C5: mov     byte ptr [ebp - 4], 2
006554C9: call    0x40291d
006554CE: cmp     eax, edi
006554D0: pop     ecx
006554D1: jge     0x6554d9
006554D3: push    eax
006554D4: call    0xa5fde4
006554D9: and     byte ptr [ebp - 4], 0
006554DD: lea     eax, [ebp - 0x3c]
006554E0: push    eax
006554E1: call    0x40291d
006554E6: cmp     eax, edi
006554E8: pop     ecx
006554E9: jge     0x6554f1
006554EB: push    eax
006554EC: call    0xa5fde4
006554F1: lea     eax, [ebp - 0x1c]
006554F4: push    eax
006554F5: mov     ecx, ebx
006554F7: call    0x426604
006554FC: mov     eax, dword ptr [eax]
006554FE: push    1
```

## Candidate near `0x00655509`
```asm
006554D9: and     byte ptr [ebp - 4], 0
006554DD: lea     eax, [ebp - 0x3c]
006554E0: push    eax
006554E1: call    0x40291d
006554E6: cmp     eax, edi
006554E8: pop     ecx
006554E9: jge     0x6554f1
006554EB: push    eax
006554EC: call    0xa5fde4
006554F1: lea     eax, [ebp - 0x1c]
006554F4: push    eax
006554F5: mov     ecx, ebx
006554F7: call    0x426604
006554FC: mov     eax, dword ptr [eax]
006554FE: push    1
00655500: push    eax
00655501: lea     ecx, [ebp - 0x3c]
00655504: call    0x410fdf
00655509: add     esi, dword ptr [ebx + 0x214]
0065550F: mov     byte ptr [ebp - 4], 5
00655513: cmp     dword ptr [esi], edi
00655515: jne     0x655521
00655517: push    0x80004003
0065551C: call    0xa5fde4
00655521: mov     eax, dword ptr [esi]
00655523: mov     ecx, dword ptr [eax]
00655525: sub     esp, 0x10
00655528: mov     edi, esp
0065552A: lea     esi, [ebp - 0x3c]
0065552D: movsd   dword ptr es:[edi], dword ptr [esi]
0065552E: movsd   dword ptr es:[edi], dword ptr [esi]
0065552F: movsd   dword ptr es:[edi], dword ptr [esi]
00655530: push    eax
00655531: mov     dword ptr [ebp - 0x14], eax
00655534: movsd   dword ptr es:[edi], dword ptr [esi]
00655535: call    dword ptr [ecx + 0x64]
00655538: test    eax, eax
0065553A: jge     0x65554a
0065553C: push    0xbd8348
00655541: push    dword ptr [ebp - 0x14]
00655544: push    eax
00655545: call    0xa5fdf2
0065554A: lea     eax, [ebp - 0x3c]
0065554D: push    eax
0065554E: mov     byte ptr [ebp - 4], 4
00655552: call    0x40291d
```

## Candidate near `0x00655589`
```asm
00655557: test    eax, eax
00655559: pop     ecx
0065555A: jge     0x655562
0065555C: push    eax
0065555D: call    0xa5fde4
00655562: and     byte ptr [ebp - 4], 0
00655566: lea     ecx, [ebp - 0x1c]
00655569: call    0x4156c5
0065556E: lea     eax, [ebp - 0x14]
00655571: push    eax
00655572: mov     ecx, ebx
00655574: call    0x426604
00655579: mov     eax, dword ptr [eax]
0065557B: push    1
0065557D: push    eax
0065557E: lea     ecx, [ebp - 0x3c]
00655581: call    0x410fdf
00655586: mov     esi, dword ptr [ebp - 0x10]
00655589: add     esi, dword ptr [ebx + 0x214]
0065558F: mov     byte ptr [ebp - 4], 7
00655593: cmp     dword ptr [esi], 0
00655596: jne     0x6555a2
00655598: push    0x80004003
0065559D: call    0xa5fde4
006555A2: mov     eax, dword ptr [esi]
006555A4: mov     ecx, dword ptr [eax]
006555A6: sub     esp, 0x10
006555A9: mov     edi, esp
006555AB: lea     esi, [ebp - 0x3c]
006555AE: movsd   dword ptr es:[edi], dword ptr [esi]
006555AF: movsd   dword ptr es:[edi], dword ptr [esi]
006555B0: movsd   dword ptr es:[edi], dword ptr [esi]
006555B1: push    eax
006555B2: mov     dword ptr [ebp - 0x1c], eax
006555B5: movsd   dword ptr es:[edi], dword ptr [esi]
006555B6: call    dword ptr [ecx + 0xfc]
006555BC: test    eax, eax
006555BE: mov     edi, 0xbd8358
006555C3: jge     0x6555cf
006555C5: push    edi
006555C6: push    dword ptr [ebp - 0x1c]
006555C9: push    eax
006555CA: call    0xa5fdf2
006555CF: lea     eax, [ebp - 0x3c]
006555D2: push    eax
006555D3: mov     byte ptr [ebp - 4], 6
```

## Candidate near `0x006555F6`
```asm
006555C3: jge     0x6555cf
006555C5: push    edi
006555C6: push    dword ptr [ebp - 0x1c]
006555C9: push    eax
006555CA: call    0xa5fdf2
006555CF: lea     eax, [ebp - 0x3c]
006555D2: push    eax
006555D3: mov     byte ptr [ebp - 4], 6
006555D7: call    0x40291d
006555DC: test    eax, eax
006555DE: pop     ecx
006555DF: jge     0x6555e7
006555E1: push    eax
006555E2: call    0xa5fde4
006555E7: and     byte ptr [ebp - 4], 0
006555EB: lea     ecx, [ebp - 0x14]
006555EE: call    0x4156c5
006555F3: mov     esi, dword ptr [ebp - 0x10]
006555F6: add     esi, dword ptr [ebx + 0x214]
006555FC: cmp     dword ptr [esi], 0
006555FF: jne     0x65560b
00655601: push    0x80004003
00655606: call    0xa5fde4
0065560B: mov     esi, dword ptr [esi]
0065560D: mov     eax, dword ptr [esi]
0065560F: push    -1
00655611: push    esi
00655612: call    dword ptr [eax + 0xe0]
00655618: test    eax, eax
0065561A: jge     0x655624
0065561C: push    edi
0065561D: push    esi
0065561E: push    eax
0065561F: call    0xa5fdf2
00655624: mov     esi, 0xbf6300
00655629: push    esi
0065562A: lea     ecx, [ebp - 0x2c]
0065562D: call    0x402f85
00655632: push    esi
00655633: lea     ecx, [ebp - 0x3c]
00655636: mov     byte ptr [ebp - 4], 8
0065563A: call    0x402f85
0065563F: mov     esi, dword ptr [ebp - 0x10]
00655642: add     esi, dword ptr [ebx + 0x214]
00655648: mov     byte ptr [ebp - 4], 9
0065564C: cmp     dword ptr [esi], 0
```

## Candidate near `0x00655642`
```asm
0065560F: push    -1
00655611: push    esi
00655612: call    dword ptr [eax + 0xe0]
00655618: test    eax, eax
0065561A: jge     0x655624
0065561C: push    edi
0065561D: push    esi
0065561E: push    eax
0065561F: call    0xa5fdf2
00655624: mov     esi, 0xbf6300
00655629: push    esi
0065562A: lea     ecx, [ebp - 0x2c]
0065562D: call    0x402f85
00655632: push    esi
00655633: lea     ecx, [ebp - 0x3c]
00655636: mov     byte ptr [ebp - 4], 8
0065563A: call    0x402f85
0065563F: mov     esi, dword ptr [ebp - 0x10]
00655642: add     esi, dword ptr [ebx + 0x214]
00655648: mov     byte ptr [ebp - 4], 9
0065564C: cmp     dword ptr [esi], 0
0065564F: jne     0x65565b
00655651: push    0x80004003
00655656: call    0xa5fde4
0065565B: mov     edi, dword ptr [ebx + 0x818]
00655661: mov     eax, dword ptr [ebp + 8]
00655664: cdq     
00655665: idiv    edi
00655667: mov     esi, dword ptr [esi]
00655669: mov     dword ptr [ebp - 0x14], esi
0065566C: sub     esp, 0x10
0065566F: mov     ecx, eax
00655671: mov     eax, dword ptr [ebp + 8]
00655674: imul    ecx, ecx, 0x43
00655677: cdq     
00655678: idiv    edi
0065567A: mov     eax, dword ptr [esi]
0065567C: add     ecx, dword ptr [ebx + 0x820]
00655682: mov     edi, esp
00655684: lea     esi, [ebp - 0x2c]
00655687: movsd   dword ptr es:[edi], dword ptr [esi]
00655688: movsd   dword ptr es:[edi], dword ptr [esi]
00655689: movsd   dword ptr es:[edi], dword ptr [esi]
0065568A: movsd   dword ptr es:[edi], dword ptr [esi]
0065568B: sub     esp, 0x10
0065568E: mov     edi, esp
```

## Candidate near `0x006557D4`
```asm
0065579F: mov     ecx, eax
006557A1: mov     byte ptr [ebp - 4], 0x10
006557A5: call    0x4032b2
006557AA: cmp     eax, edi
006557AC: mov     dword ptr [ebp - 0x1c], eax
006557AF: mov     dword ptr [ebp + 8], edi
006557B2: je      0x6557d1
006557B4: lea     eax, [ebp - 0x1c]
006557B7: push    eax
006557B8: lea     ecx, [ebp + 8]
006557BB: call    0x41e527
006557C0: cmp     eax, edi
006557C2: jge     0x6557d1
006557C4: cmp     eax, 0x80004002
006557C9: je      0x6557d1
006557CB: push    eax
006557CC: call    0xa5fde4
006557D1: mov     eax, dword ptr [ebp - 0x10]
006557D4: add     eax, dword ptr [ebx + 0x214]
006557DA: mov     esi, dword ptr [ebp + 8]
006557DD: mov     ebx, eax
006557DF: cmp     dword ptr [ebx], edi
006557E1: mov     byte ptr [ebp - 4], 0x11
006557E5: jne     0x6557f1
006557E7: push    0x80004003
006557EC: call    0xa5fde4
006557F1: mov     ecx, dword ptr [ebx]
006557F3: lea     eax, [ebp - 0x6c]
006557F6: push    eax
006557F7: lea     eax, [ebp - 0x5c]
006557FA: push    eax
006557FB: lea     eax, [ebp - 0x4c]
006557FE: push    eax
006557FF: lea     eax, [ebp - 0x2c]
00655802: push    eax
00655803: lea     eax, [ebp - 0x3c]
00655806: push    eax
00655807: push    esi
00655808: lea     eax, [ebp - 0x7c]
0065580B: push    eax
0065580C: call    0x426bab
00655811: lea     eax, [ebp - 0x7c]
00655814: push    eax
00655815: call    0x40291d
0065581A: cmp     eax, edi
0065581C: pop     ecx
```

## Candidate near `0x0065595C`
```asm
00655933: pop     ecx
00655934: jge     0x65593c
00655936: push    eax
00655937: call    0xa5fde4
0065593C: and     dword ptr [ebp - 4], 0
00655940: lea     eax, [ebp - 0x24]
00655943: push    eax
00655944: call    esi
00655946: lea     eax, [ebp - 0x24]
00655949: push    edi
0065594A: push    eax
0065594B: call    0x402b8c
00655950: test    eax, eax
00655952: pop     ecx
00655953: pop     ecx
00655954: jge     0x65595c
00655956: push    eax
00655957: call    0xa5fde4
0065595C: mov     eax, dword ptr [ebx + 0x214]
00655962: mov     edi, dword ptr [ebp + 8]
00655965: cmp     dword ptr [eax + edi*4], 0
00655969: lea     esi, [eax + edi*4]
0065596C: mov     byte ptr [ebp - 4], 1
00655970: jne     0x65597c
00655972: push    0x80004003
00655977: call    0xa5fde4
0065597C: mov     ecx, dword ptr [esi]
0065597E: mov     esi, dword ptr [ebx + 0x818]
00655984: mov     eax, edi
00655986: cdq     
00655987: idiv    esi
00655989: mov     edx, dword ptr [ebx + 0x820]
0065598F: sub     esp, 0x10
00655992: mov     dword ptr [ebp - 0x14], ecx
00655995: imul    eax, eax, 0x43
00655998: lea     eax, [eax + edx + 2]
0065599C: mov     dword ptr [ebp - 0x10], eax
0065599F: mov     eax, edi
006559A1: cdq     
006559A2: idiv    esi
006559A4: mov     eax, dword ptr [ebx + 0x81c]
006559AA: mov     edi, esp
006559AC: lea     esi, [ebp - 0x34]
006559AF: movsd   dword ptr es:[edi], dword ptr [esi]
006559B0: movsd   dword ptr es:[edi], dword ptr [esi]
006559B1: movsd   dword ptr es:[edi], dword ptr [esi]
```

## Candidate near `0x00655AB2`
```asm
00655A84: jge     0x655a8c
00655A86: push    eax
00655A87: call    0xa5fde4
00655A8C: and     dword ptr [ebp - 4], 0
00655A90: lea     eax, [ebp - 0x20]
00655A93: push    eax
00655A94: call    esi
00655A96: lea     eax, [ebp - 0x20]
00655A99: push    edi
00655A9A: push    eax
00655A9B: call    0x402b8c
00655AA0: test    eax, eax
00655AA2: pop     ecx
00655AA3: pop     ecx
00655AA4: jge     0x655aac
00655AA6: push    eax
00655AA7: call    0xa5fde4
00655AAC: mov     eax, dword ptr [ebx + 0x1d0]
00655AB2: mov     ecx, dword ptr [ebx + 0x214]
00655AB8: cmp     dword ptr [ecx + eax*4], 0
00655ABC: lea     esi, [ecx + eax*4]
00655ABF: mov     byte ptr [ebp - 4], 1
00655AC3: jne     0x655acf
00655AC5: push    0x80004003
00655ACA: call    0xa5fde4
00655ACF: mov     edi, dword ptr [ebx + 0x1d0]
00655AD5: mov     ecx, dword ptr [ebx + 0x818]
00655ADB: mov     eax, edi
00655ADD: cdq     
00655ADE: idiv    ecx
00655AE0: mov     esi, dword ptr [esi]
00655AE2: mov     dword ptr [ebp - 0x10], esi
00655AE5: sub     esp, 0x10
00655AE8: mov     ecx, eax
00655AEA: mov     eax, edi
00655AEC: imul    ecx, ecx, 0x43
00655AEF: cdq     
00655AF0: idiv    dword ptr [ebx + 0x818]
00655AF6: mov     eax, dword ptr [esi]
00655AF8: add     ecx, dword ptr [ebx + 0x820]
00655AFE: mov     edi, esp
00655B00: lea     esi, [ebp - 0x30]
00655B03: movsd   dword ptr es:[edi], dword ptr [esi]
00655B04: movsd   dword ptr es:[edi], dword ptr [esi]
00655B05: movsd   dword ptr es:[edi], dword ptr [esi]
00655B06: movsd   dword ptr es:[edi], dword ptr [esi]
```

## Candidate near `0x00655BAD`
```asm
00655B7B: pop     esi
00655B7C: mov     dword ptr fs:[0], ecx
00655B83: pop     ebx
00655B84: leave   
00655B85: ret     
00655B86: mov     eax, 0xaa0414
00655B8B: call    0xa60b98
00655B90: sub     esp, 0xfc
00655B96: push    ebx
00655B97: push    esi
00655B98: push    edi
00655B99: mov     esi, ecx
00655B9B: xor     edi, edi
00655B9D: mov     dword ptr [ebp - 0x18], esi
00655BA0: mov     dword ptr [ebp - 0x24], edi
00655BA3: mov     eax, dword ptr [esi + 0x780]
00655BA9: lea     edx, [ebp - 0x19]
00655BAC: push    edx
00655BAD: lea     ecx, [esi + 0x214]
00655BB3: push    eax
00655BB4: mov     dword ptr [ebp - 4], edi
00655BB7: call    0x446258
00655BBC: cmp     dword ptr [esi + 0x780], edi
00655BC2: mov     dword ptr [ebp - 0x14], edi
00655BC5: jle     0x65611a
00655BCB: mov     ebx, 0xbf6300
00655BD0: jmp     0x655bd4
00655BD2: xor     edi, edi
00655BD4: lea     eax, [ebp - 0x2c]
00655BD7: push    0x158b
00655BDC: push    eax
00655BDD: call    0x79e805
00655BE2: mov     ecx, eax
00655BE4: call    0x406455
00655BE9: mov     ecx, dword ptr [eax]
00655BEB: mov     eax, dword ptr [ebp - 0x14]
00655BEE: mov     edx, dword ptr [esi + 0x210]
00655BF4: shl     eax, 2
00655BF7: push    dword ptr [edx + eax]
00655BFA: mov     dword ptr [ebp - 0x10], eax
00655BFD: push    ecx
00655BFE: lea     eax, [ebp - 0x24]
00655C01: push    eax
00655C02: mov     byte ptr [ebp - 4], 1
00655C06: call    0x445b4b
00655C0B: mov     eax, dword ptr [ebp - 0x2c]
```

## Candidate near `0x00655C74`
```asm
00655C3E: cmp     dword ptr [0xbf14ec], edi
00655C44: mov     byte ptr [ebp - 4], 3
00655C48: jne     0x655c54
00655C4A: push    0x80004003
00655C4F: call    0xa5fde4
00655C54: mov     ecx, dword ptr [0xbf14ec]
00655C5A: lea     eax, [ebp - 0xb8]
00655C60: push    eax
00655C61: lea     eax, [ebp - 0x48]
00655C64: push    eax
00655C65: push    4
00655C67: push    edi
00655C68: push    edi
00655C69: push    edi
00655C6A: push    edi
00655C6B: lea     eax, [ebp - 0x34]
00655C6E: push    eax
00655C6F: call    0x426c7e
00655C74: mov     ecx, dword ptr [esi + 0x214]
00655C7A: add     ecx, dword ptr [ebp - 0x10]
00655C7D: push    dword ptr [eax]
00655C7F: lea     edi, [esi + 0x214]
00655C85: call    0x428712
00655C8A: lea     ecx, [ebp - 0x34]
00655C8D: call    0x4156c5
00655C92: lea     eax, [ebp - 0x48]
00655C95: push    eax
00655C96: mov     byte ptr [ebp - 4], 2
00655C9A: call    0x40291d
00655C9F: test    eax, eax
00655CA1: pop     ecx
00655CA2: jge     0x655caa
00655CA4: push    eax
00655CA5: call    0xa5fde4
00655CAA: and     byte ptr [ebp - 4], 0
00655CAE: lea     eax, [ebp - 0xb8]
00655CB4: push    eax
00655CB5: call    0x40291d
00655CBA: test    eax, eax
00655CBC: pop     ecx
00655CBD: jge     0x655cc5
00655CBF: push    eax
00655CC0: call    0xa5fde4
00655CC5: lea     eax, [ebp - 0x28]
00655CC8: push    eax
00655CC9: mov     ecx, esi
```

## Candidate near `0x00655C7F`
```asm
00655C4A: push    0x80004003
00655C4F: call    0xa5fde4
00655C54: mov     ecx, dword ptr [0xbf14ec]
00655C5A: lea     eax, [ebp - 0xb8]
00655C60: push    eax
00655C61: lea     eax, [ebp - 0x48]
00655C64: push    eax
00655C65: push    4
00655C67: push    edi
00655C68: push    edi
00655C69: push    edi
00655C6A: push    edi
00655C6B: lea     eax, [ebp - 0x34]
00655C6E: push    eax
00655C6F: call    0x426c7e
00655C74: mov     ecx, dword ptr [esi + 0x214]
00655C7A: add     ecx, dword ptr [ebp - 0x10]
00655C7D: push    dword ptr [eax]
00655C7F: lea     edi, [esi + 0x214]
00655C85: call    0x428712
00655C8A: lea     ecx, [ebp - 0x34]
00655C8D: call    0x4156c5
00655C92: lea     eax, [ebp - 0x48]
00655C95: push    eax
00655C96: mov     byte ptr [ebp - 4], 2
00655C9A: call    0x40291d
00655C9F: test    eax, eax
00655CA1: pop     ecx
00655CA2: jge     0x655caa
00655CA4: push    eax
00655CA5: call    0xa5fde4
00655CAA: and     byte ptr [ebp - 4], 0
00655CAE: lea     eax, [ebp - 0xb8]
00655CB4: push    eax
00655CB5: call    0x40291d
00655CBA: test    eax, eax
00655CBC: pop     ecx
00655CBD: jge     0x655cc5
00655CBF: push    eax
00655CC0: call    0xa5fde4
00655CC5: lea     eax, [ebp - 0x28]
00655CC8: push    eax
00655CC9: mov     ecx, esi
00655CCB: call    0x426604
00655CD0: mov     eax, dword ptr [eax]
00655CD2: push    1
```

## Candidate near `0x00655D60`
```asm
00655D2B: test    eax, eax
00655D2D: pop     ecx
00655D2E: jge     0x655d36
00655D30: push    eax
00655D31: call    0xa5fde4
00655D36: and     byte ptr [ebp - 4], 0
00655D3A: lea     ecx, [ebp - 0x28]
00655D3D: call    0x4156c5
00655D42: mov     esi, dword ptr [ebp - 0x18]
00655D45: lea     eax, [ebp - 0x30]
00655D48: push    eax
00655D49: mov     ecx, esi
00655D4B: call    0x426604
00655D50: mov     eax, dword ptr [eax]
00655D52: push    1
00655D54: push    eax
00655D55: lea     ecx, [ebp - 0xe8]
00655D5B: call    0x410fdf
00655D60: lea     eax, [esi + 0x214]
00655D66: mov     esi, dword ptr [eax]
00655D68: mov     eax, dword ptr [ebp - 0x14]
00655D6B: shl     eax, 2
00655D6E: add     esi, eax
00655D70: cmp     dword ptr [esi], 0
00655D73: mov     byte ptr [ebp - 4], 7
00655D77: jne     0x655d83
00655D79: push    0x80004003
00655D7E: call    0xa5fde4
00655D83: mov     eax, dword ptr [esi]
00655D85: mov     ecx, dword ptr [eax]
00655D87: sub     esp, 0x10
00655D8A: mov     edi, esp
00655D8C: lea     esi, [ebp - 0xe8]
00655D92: movsd   dword ptr es:[edi], dword ptr [esi]
00655D93: movsd   dword ptr es:[edi], dword ptr [esi]
00655D94: movsd   dword ptr es:[edi], dword ptr [esi]
00655D95: push    eax
00655D96: mov     dword ptr [ebp - 0x10], eax
00655D99: movsd   dword ptr es:[edi], dword ptr [esi]
00655D9A: call    dword ptr [ecx + 0xfc]
00655DA0: test    eax, eax
00655DA2: jge     0x655db2
00655DA4: push    0xbd8358
00655DA9: push    dword ptr [ebp - 0x10]
00655DAC: push    eax
00655DAD: call    0xa5fdf2
```

## Candidate near `0x00655DDC`
```asm
00655DA2: jge     0x655db2
00655DA4: push    0xbd8358
00655DA9: push    dword ptr [ebp - 0x10]
00655DAC: push    eax
00655DAD: call    0xa5fdf2
00655DB2: lea     eax, [ebp - 0xe8]
00655DB8: push    eax
00655DB9: mov     byte ptr [ebp - 4], 6
00655DBD: call    0x40291d
00655DC2: test    eax, eax
00655DC4: pop     ecx
00655DC5: jge     0x655dcd
00655DC7: push    eax
00655DC8: call    0xa5fde4
00655DCD: and     byte ptr [ebp - 4], 0
00655DD1: lea     ecx, [ebp - 0x30]
00655DD4: call    0x4156c5
00655DD9: mov     eax, dword ptr [ebp - 0x18]
00655DDC: mov     esi, dword ptr [eax + 0x214]
00655DE2: lea     edi, [eax + 0x214]
00655DE8: mov     eax, dword ptr [ebp - 0x14]
00655DEB: shl     eax, 2
00655DEE: add     esi, eax
00655DF0: cmp     dword ptr [esi], 0
00655DF3: mov     dword ptr [ebp - 0x10], eax
00655DF6: jne     0x655e02
00655DF8: push    0x80004003
00655DFD: call    0xa5fde4
00655E02: mov     esi, dword ptr [esi]
00655E04: mov     eax, dword ptr [esi]
00655E06: push    -1
00655E08: push    esi
00655E09: call    dword ptr [eax + 0xe0]
00655E0F: test    eax, eax
00655E11: jge     0x655e1f
00655E13: push    0xbd8358
00655E18: push    esi
00655E19: push    eax
00655E1A: call    0xa5fdf2
00655E1F: push    ebx
00655E20: lea     ecx, [ebp - 0xd8]
00655E26: call    0x402f85
00655E2B: push    ebx
00655E2C: lea     ecx, [ebp - 0x98]
00655E32: mov     byte ptr [ebp - 4], 8
00655E36: call    0x402f85
```

## Candidate near `0x00655DE2`
```asm
00655DA4: push    0xbd8358
00655DA9: push    dword ptr [ebp - 0x10]
00655DAC: push    eax
00655DAD: call    0xa5fdf2
00655DB2: lea     eax, [ebp - 0xe8]
00655DB8: push    eax
00655DB9: mov     byte ptr [ebp - 4], 6
00655DBD: call    0x40291d
00655DC2: test    eax, eax
00655DC4: pop     ecx
00655DC5: jge     0x655dcd
00655DC7: push    eax
00655DC8: call    0xa5fde4
00655DCD: and     byte ptr [ebp - 4], 0
00655DD1: lea     ecx, [ebp - 0x30]
00655DD4: call    0x4156c5
00655DD9: mov     eax, dword ptr [ebp - 0x18]
00655DDC: mov     esi, dword ptr [eax + 0x214]
00655DE2: lea     edi, [eax + 0x214]
00655DE8: mov     eax, dword ptr [ebp - 0x14]
00655DEB: shl     eax, 2
00655DEE: add     esi, eax
00655DF0: cmp     dword ptr [esi], 0
00655DF3: mov     dword ptr [ebp - 0x10], eax
00655DF6: jne     0x655e02
00655DF8: push    0x80004003
00655DFD: call    0xa5fde4
00655E02: mov     esi, dword ptr [esi]
00655E04: mov     eax, dword ptr [esi]
00655E06: push    -1
00655E08: push    esi
00655E09: call    dword ptr [eax + 0xe0]
00655E0F: test    eax, eax
00655E11: jge     0x655e1f
00655E13: push    0xbd8358
00655E18: push    esi
00655E19: push    eax
00655E1A: call    0xa5fdf2
00655E1F: push    ebx
00655E20: lea     ecx, [ebp - 0xd8]
00655E26: call    0x402f85
00655E2B: push    ebx
00655E2C: lea     ecx, [ebp - 0x98]
00655E32: mov     byte ptr [ebp - 4], 8
00655E36: call    0x402f85
00655E3B: mov     esi, dword ptr [edi]
```

## Candidate near `0x00655FE8`
```asm
00655FB2: mov     ecx, eax
00655FB4: mov     byte ptr [ebp - 4], 0x10
00655FB8: call    0x4032b2
00655FBD: and     dword ptr [ebp - 0x20], 0
00655FC1: test    eax, eax
00655FC3: mov     dword ptr [ebp - 0x38], eax
00655FC6: je      0x655fe5
00655FC8: lea     eax, [ebp - 0x38]
00655FCB: push    eax
00655FCC: lea     ecx, [ebp - 0x20]
00655FCF: call    0x41e527
00655FD4: test    eax, eax
00655FD6: jge     0x655fe5
00655FD8: cmp     eax, 0x80004002
00655FDD: je      0x655fe5
00655FDF: push    eax
00655FE0: call    0xa5fde4
00655FE5: mov     eax, dword ptr [ebp - 0x18]
00655FE8: mov     esi, dword ptr [eax + 0x214]
00655FEE: mov     edi, dword ptr [ebp - 0x20]
00655FF1: add     eax, 0x214
00655FF6: mov     eax, dword ptr [ebp - 0x14]
00655FF9: shl     eax, 2
00655FFC: add     esi, eax
00655FFE: cmp     dword ptr [esi], 0
00656001: mov     byte ptr [ebp - 4], 0x11
00656005: jne     0x656011
00656007: push    0x80004003
0065600C: call    0xa5fde4
00656011: mov     esi, dword ptr [esi]
00656013: lea     eax, [ebp - 0xc8]
00656019: push    eax
0065601A: lea     eax, [ebp - 0xa8]
00656020: push    eax
00656021: lea     eax, [ebp - 0x88]
00656027: push    eax
00656028: lea     eax, [ebp - 0x68]
0065602B: push    eax
0065602C: lea     eax, [ebp - 0x58]
0065602F: push    eax
00656030: push    edi
00656031: lea     eax, [ebp - 0xf8]
00656037: push    eax
00656038: mov     ecx, esi
0065603A: call    0x426bab
0065603F: lea     eax, [ebp - 0xf8]
```

## Candidate near `0x0067F181`
```asm
0067F142: push    eax
0067F143: lea     ecx, [ebp - 0x78]
0067F146: mov     byte ptr [ebp - 4], 0xa3
0067F14A: call    0x40263b
0067F14F: mov     ecx, eax
0067F151: call    0x403935
0067F156: mov     dword ptr [ebp - 0x90], 1
0067F160: push    eax
0067F161: mov     byte ptr [ebp - 4], 0xa5
0067F165: call    0x414d40
0067F16A: pop     ecx
0067F16B: pop     ecx
0067F16C: mov     esi, eax
0067F16E: jmp     0x67f172
0067F170: xor     esi, esi
0067F172: lea     ecx, [ebp - 0x18]
0067F175: call    0x681e8e
0067F17A: test    byte ptr [ebp - 0x90], 1
0067F181: mov     dword ptr [eax + 0x214], esi
0067F187: mov     dword ptr [ebp - 4], 0xa3
0067F18E: je      0x67f198
0067F190: lea     ecx, [ebp - 0x74]
0067F193: call    0x403923
0067F198: push    ebx
0067F199: push    ebx
0067F19A: push    ecx
0067F19B: mov     eax, esp
0067F19D: mov     dword ptr [ebp - 0x38], esp
0067F1A0: push    0x10b2
0067F1A5: push    eax
0067F1A6: call    0x79e805
0067F1AB: mov     ecx, eax
0067F1AD: call    0x406292
0067F1B2: lea     eax, [ebp - 0x74]
0067F1B5: push    eax
0067F1B6: lea     ecx, [ebp - 0x10]
0067F1B9: mov     byte ptr [ebp - 4], 0xa3
0067F1BD: call    0x40263b
0067F1C2: mov     ecx, eax
0067F1C4: call    0x403935
0067F1C9: mov     ecx, eax
0067F1CB: mov     byte ptr [ebp - 4], 0xa7
0067F1CF: call    0x4032b2
0067F1D4: mov     dword ptr [ebp - 0x48], eax
0067F1D7: lea     eax, [ebp - 0x48]
0067F1DA: push    eax
```

## Candidate near `0x006E35E1`
```asm
006E359C: push    ecx
006E359D: push    esi
006E359E: mov     esi, ecx
006E35A0: mov     dword ptr [esi - 8], 0xafcb90
006E35A7: mov     dword ptr [esi - 4], 0xafcb44
006E35AE: mov     dword ptr [ebp - 0x10], esi
006E35B1: mov     dword ptr [esi], 0xafcb40
006E35B7: mov     eax, dword ptr [esi + 0xae8]
006E35BD: test    eax, eax
006E35BF: mov     dword ptr [ebp - 4], 0x1b
006E35C6: je      0x6e35d2
006E35C8: add     eax, -0xc
006E35CB: push    eax
006E35CC: call    0x428d13
006E35D1: pop     ecx
006E35D2: lea     ecx, [esi + 0x218]
006E35D8: mov     byte ptr [ebp - 4], 0x1a
006E35DC: call    0x8e6ba3
006E35E1: lea     ecx, [esi + 0x214]
006E35E7: call    0x45baee
006E35EC: lea     ecx, [esi + 0x200]
006E35F2: mov     byte ptr [ebp - 4], 0x18
006E35F6: mov     dword ptr [ecx], 0xafcbfc
006E35FC: call    0x6e9c88
006E3601: lea     ecx, [esi + 0x1fc]
006E3607: call    0x4156c5
006E360C: mov     eax, dword ptr [esi + 0x1f8]
006E3612: test    eax, eax
006E3614: mov     byte ptr [ebp - 4], 0x16
006E3618: je      0x6e3620
006E361A: mov     ecx, dword ptr [eax]
006E361C: push    eax
006E361D: call    dword ptr [ecx + 8]
006E3620: mov     eax, dword ptr [esi + 0x1f4]
006E3626: test    eax, eax
006E3628: mov     byte ptr [ebp - 4], 0x15
006E362C: je      0x6e3634
006E362E: mov     ecx, dword ptr [eax]
006E3630: push    eax
006E3631: call    dword ptr [ecx + 8]
006E3634: mov     eax, dword ptr [esi + 0x1f0]
006E363A: test    eax, eax
006E363C: mov     byte ptr [ebp - 4], 0x14
006E3640: je      0x6e3648
006E3642: mov     ecx, dword ptr [eax]
006E3644: push    eax
```

## Candidate near `0x006E6F30`
```asm
006E6EED: mov     dword ptr fs:[0], ecx
006E6EF4: pop     ebx
006E6EF5: leave   
006E6EF6: ret     4
006E6EF9: mov     eax, 0xaab547
006E6EFE: call    0xa60b98
006E6F03: sub     esp, 0x54
006E6F06: and     dword ptr [ebp - 0x10], 0
006E6F0A: push    ebx
006E6F0B: push    esi
006E6F0C: mov     ebx, ecx
006E6F0E: push    edi
006E6F0F: mov     dword ptr [ebp - 0x14], ebx
006E6F12: and     dword ptr [ebp - 4], 0
006E6F16: cmp     dword ptr [ebx + 0xadc], 2
006E6F1D: jne     0x6e70a1
006E6F23: cmp     dword ptr [ebx + 0xb00], 1
006E6F2A: je      0x6e70a1
006E6F30: mov     eax, dword ptr [ebx + 0x214]
006E6F36: test    eax, eax
006E6F38: je      0x6e70a1
006E6F3E: jmp     0x6e6f43
006E6F40: mov     eax, dword ptr [ebp - 0x18]
006E6F43: mov     ecx, eax
006E6F45: mov     edx, eax
006E6F47: add     eax, -0x10
006E6F4A: neg     edx
006E6F4C: sbb     edx, edx
006E6F4E: and     edx, eax
006E6F50: mov     eax, dword ptr [edx + 4]
006E6F53: mov     edx, eax
006E6F55: add     eax, 0x10
006E6F58: neg     edx
006E6F5A: sbb     edx, edx
006E6F5C: and     edx, eax
006E6F5E: push    ecx
006E6F5F: lea     ecx, [ebp - 0x30]
006E6F62: mov     dword ptr [ebp - 0x18], edx
006E6F65: call    0x6e4428
006E6F6A: mov     eax, dword ptr [ebp - 0x28]
006E6F6D: cmp     eax, dword ptr [ebp + 0xc]
006E6F70: mov     byte ptr [ebp - 4], 1
006E6F74: jne     0x6e708b
006E6F7A: push    3
006E6F7C: push    -2
006E6F7E: lea     ecx, [ebp - 0x40]
```

## Candidate near `0x006FA3AF`
```asm
006FA355: lea     ecx, [esi + 0x244]
006FA35B: mov     byte ptr [ebp - 4], 0x14
006FA35F: call    0x428951
006FA364: lea     ecx, [esi + 0x23c]
006FA36A: mov     byte ptr [ebp - 4], 0x13
006FA36E: call    0x473def
006FA373: lea     ecx, [esi + 0x234]
006FA379: mov     byte ptr [ebp - 4], 0x12
006FA37D: call    0x428925
006FA382: lea     ecx, [esi + 0x22c]
006FA388: mov     byte ptr [ebp - 4], 0x11
006FA38C: call    0x428925
006FA391: lea     ecx, [esi + 0x224]
006FA397: mov     byte ptr [ebp - 4], 0x10
006FA39B: call    0x428925
006FA3A0: lea     ecx, [esi + 0x21c]
006FA3A6: mov     byte ptr [ebp - 4], 0xf
006FA3AA: call    0x428925
006FA3AF: lea     ecx, [esi + 0x214]
006FA3B5: mov     byte ptr [ebp - 4], 0xe
006FA3B9: call    0x428925
006FA3BE: push    0x4284fa
006FA3C3: push    3
006FA3C5: push    8
006FA3C7: lea     eax, [esi + 0x1fc]
006FA3CD: push    eax
006FA3CE: mov     byte ptr [ebp - 4], 0xd
006FA3D2: call    0xa61098
006FA3D7: lea     ecx, [esi + 0x1f4]
006FA3DD: mov     byte ptr [ebp - 4], 0xc
006FA3E1: call    0x428925
006FA3E6: lea     ecx, [esi + 0x1ec]
006FA3EC: mov     byte ptr [ebp - 4], 0xb
006FA3F0: call    0x428925
006FA3F5: lea     ecx, [esi + 0x1e4]
006FA3FB: mov     byte ptr [ebp - 4], 0xa
006FA3FF: call    0x428925
006FA404: lea     ecx, [esi + 0x1dc]
006FA40A: mov     byte ptr [ebp - 4], 9
006FA40E: call    0x428925
006FA413: lea     ecx, [esi + 0x1d4]
006FA419: mov     byte ptr [ebp - 4], 8
006FA41D: call    0x428925
006FA422: lea     ecx, [esi + 0x1cc]
006FA428: mov     byte ptr [ebp - 4], 7
006FA42C: call    0x428925
```

## Candidate near `0x006FAB63`
```asm
006FAB31: call    dword ptr [eax + 0x20]
006FAB34: mov     eax, dword ptr [esi + 0x210]
006FAB3A: lea     ecx, [eax + 4]
006FAB3D: mov     eax, dword ptr [ecx]
006FAB3F: push    0
006FAB41: call    dword ptr [eax + 0x24]
006FAB44: push    ebx
006FAB45: mov     ecx, edi
006FAB47: call    0x403065
006FAB4C: mov     dword ptr [ebp - 0x14], eax
006FAB4F: test    eax, eax
006FAB51: mov     byte ptr [ebp - 4], 0x1a
006FAB55: je      0x6fab60
006FAB57: mov     ecx, eax
006FAB59: call    0x4258e4
006FAB5E: jmp     0x6fab62
006FAB60: xor     eax, eax
006FAB62: push    eax
006FAB63: lea     ecx, [esi + 0x214]
006FAB69: mov     byte ptr [ebp - 4], 6
006FAB6D: call    0x4284ff
006FAB72: mov     ecx, dword ptr [esi + 0x218]
006FAB78: mov     eax, dword ptr [ecx]
006FAB7A: lea     edx, [ebp - 0x24]
006FAB7D: push    edx
006FAB7E: push    0
006FAB80: push    0x75
006FAB82: push    0x1f9
006FAB87: push    0x3f1
006FAB8C: push    esi
006FAB8D: call    dword ptr [eax + 0x20]
006FAB90: mov     eax, dword ptr [esi + 0x218]
006FAB96: lea     ecx, [eax + 4]
006FAB99: mov     eax, dword ptr [ecx]
006FAB9B: push    0
006FAB9D: call    dword ptr [eax + 0x24]
006FABA0: lea     eax, [ebp - 0x10]
006FABA3: push    0xa37
006FABA8: push    eax
006FABA9: call    0x79e805
006FABAE: mov     ecx, eax
006FABB0: call    0x406276
006FABB5: push    eax
006FABB6: lea     ecx, [ebp - 0x18]
006FABB9: mov     byte ptr [ebp - 4], 0x1b
006FABBD: call    0x41cf93
```

## Small immediate writes in login/selector region

- `005E0AB3: and dword ptr [ebp - 4], 0`
- `005E0AC1: mov byte ptr [ebp - 4], 1`
- `005E0BC2: and dword ptr [ebp - 4], 0`
- `005E0BD0: mov byte ptr [ebp - 4], 1`
- `005E0C38: and dword ptr [esi + 0x20], 0`
- `005E0C3C: and dword ptr [esi + 0x24], 0`
- `005E0C40: and dword ptr [esi + 0x28], 0`
- `005E0C9B: and dword ptr [esi + 0x40], 0`
- `005E0C9F: and dword ptr [esi + 0x44], 0`
- `005E0CF3: and dword ptr [esi + 0x10], 0`
- `005E0F31: and dword ptr [ebp - 4], 0`
- `005E0F3F: mov byte ptr [ebp - 4], 1`
- `005E103E: and dword ptr [esi + 0x10], 0`
- `005E1042: and dword ptr [esi + 0xc], 0`
- `005E1046: and dword ptr [esi + 8], 0`
- `005E1091: and dword ptr [edi + 4], 0`
- `005E1095: and dword ptr [edi + 0xc], 0`
- `005E10B7: and dword ptr [esi + 0x10], 0`
- `005E10BB: and dword ptr [esi + 0x14], 0`
- `005E115F: and dword ptr [esi + 0x10], 0`
- `005E1248: and dword ptr [esi + 0x10], 0`
- `005E124C: and dword ptr [esi + 0xc], 0`
- `005E1250: and dword ptr [esi + 8], 0`
- `005E12BE: mov byte ptr [ebp - 4], 2`
- `005E16D9: mov dword ptr [ebp - 4], 1`
- `005E171E: mov dword ptr [ebp - 4], 2`
- `005E1733: mov byte ptr [ebp - 4], 1`
- `005E1742: and byte ptr [ebp - 4], 0`
- `005E1746: cmp dword ptr [esi + 8], 0`
- `005E1758: and dword ptr [edi + 4], 0`
- `005E1794: mov dword ptr [ebp - 4], 1`
- `005E17DF: mov dword ptr [ebp - 4], 1`
- `005E17EB: and byte ptr [ebp - 4], 0`
- `005E1834: mov dword ptr [ebp - 4], 1`
- `005E188D: mov byte ptr [ebp - 4], 6`
- `005E18A2: mov byte ptr [ebp - 4], 5`
- `005E18B7: mov byte ptr [ebp - 4], 4`
- `005E18C6: mov byte ptr [ebp - 4], 3`
- `005E18D5: mov byte ptr [ebp - 4], 2`
- `005E18E1: mov byte ptr [ebp - 4], 1`
- `005E18F6: and dword ptr [esi + 0x14], 0`
- `005E1927: mov dword ptr [ebp - 4], 1`
- `005E1977: and dword ptr [ebp - 4], 0`
- `005E1984: mov byte ptr [ebp - 4], 2`
- `005E1990: mov byte ptr [ebp - 4], 1`
- `005E19D9: mov dword ptr [ebp - 4], 1`
- `005E1AB4: mov dword ptr [ebp - 4], 1`
- `005E1AF5: and dword ptr [ebp - 4], 0`
- `005E1BDE: mov dword ptr [ebp - 4], 1`
- `005E1C24: cmp dword ptr [esi + 4], 0`
- `005E1C33: and dword ptr [esi + 4], 0`
- `005E1C76: and dword ptr [eax + 0x10], 0`
- `005E1C7A: and dword ptr [eax + 0x18], 0`
- `005E1CDD: and dword ptr [eax + 0x10], 0`
- `005E1CE1: and dword ptr [eax + 0x18], 0`
- `005E1D3B: cmp dword ptr [esi + 4], 0`
- `005E1D4A: and dword ptr [esi + 4], 0`
- `005E1D6A: cmp dword ptr [esi + 4], 0`
- `005E1D79: and dword ptr [esi + 4], 0`
- `005E1D99: cmp dword ptr [esi + 4], 0`
- `005E1DA8: and dword ptr [esi + 4], 0`
- `005E1DC8: cmp dword ptr [esi + 4], 0`
- `005E1DD7: and dword ptr [esi + 4], 0`
- `005E20CA: and dword ptr [ebp - 4], 0`
- `005E20CE: cmp dword ptr [edi + 0x10], 0`
- `005E20E0: and dword ptr [esi + 4], 0`
- `005E2118: and dword ptr [ebp - 4], 0`
- `005E211C: cmp dword ptr [edi + 0x10], 0`
- `005E212E: and dword ptr [esi + 4], 0`
- `005E215F: and dword ptr [ebp - 4], 0`
- `005E2163: cmp dword ptr [edi + 0x10], 0`
- `005E2175: and dword ptr [esi + 4], 0`
- `005E21A5: and dword ptr [ebp - 4], 0`
- `005E21E5: mov dword ptr [ebp - 4], 1`
- `005E21F1: and byte ptr [ebp - 4], 0`
- `005E2221: and dword ptr [ebp - 4], 0`
- `005E225F: and dword ptr [ebp - 4], 0`
- `005E2263: cmp dword ptr [edi + 0x10], 0`
- `005E2275: and dword ptr [esi + 4], 0`
- `005E22A6: and dword ptr [ebp - 4], 0`
- `005E22AA: cmp dword ptr [edi + 0x10], 0`
- `005E22BC: and dword ptr [esi + 4], 0`
- `005E22ED: and dword ptr [ebp - 4], 0`
- `005E22F1: cmp dword ptr [edi + 0x10], 0`
- `005E2303: and dword ptr [esi + 4], 0`
- `005E2334: and dword ptr [ebp - 4], 0`
- `005E2338: cmp dword ptr [edi + 0x10], 0`
- `005E234A: and dword ptr [esi + 4], 0`
- `005E237B: and dword ptr [ebp - 4], 0`
- `005E237F: cmp dword ptr [edi + 0x10], 0`
- `005E2391: and dword ptr [esi + 4], 0`
- `005E23C2: and dword ptr [ebp - 4], 0`
- `005E23C6: cmp dword ptr [edi + 0x10], 0`
- `005E23D8: and dword ptr [esi + 4], 0`
- `005E2409: and dword ptr [ebp - 4], 0`
- `005E240D: cmp dword ptr [edi + 0x10], 0`
- `005E241F: and dword ptr [esi + 4], 0`
- `005E2450: and dword ptr [ebp - 4], 0`
- `005E2454: cmp dword ptr [edi + 0x10], 0`
- `005E2466: and dword ptr [esi + 4], 0`
- `005E2497: and dword ptr [ebp - 4], 0`
- `005E249B: cmp dword ptr [edi + 0x10], 0`
- `005E24AD: and dword ptr [esi + 4], 0`
- `005E25FC: cmp dword ptr [esi + 4], 0`
- `005E26EC: and dword ptr [edi], 0`
- `005E27F0: cmp dword ptr [esi + 4], 0`
- `005E27FD: and dword ptr [esi + 4], 0`
- `005E281F: and dword ptr [esi], 0`
- `005E2964: cmp dword ptr [esi + 4], 0`
- `005E2A54: and dword ptr [edi], 0`
- `005E2B73: cmp dword ptr [esi + 4], 0`
- `005E2C42: cmp dword ptr [esi + 4], 0`
- `005E2D32: cmp dword ptr [esi + 4], 0`
- `005E2D66: and dword ptr [ebp + 8], 0`
- `005E2D83: and dword ptr [ebp - 4], 0`
- `005E2D97: and dword ptr [esi + 8], 0`
- `005E2DA2: mov byte ptr [ebp - 4], 1`
- `005E2DAB: and dword ptr [esi + 0xc], 0`
- `005E2DB6: mov byte ptr [ebp - 4], 2`
- `005E2E10: cmp dword ptr [esi + 4], 0`
- `005E2EB7: cmp dword ptr [esi + 4], 0`
- `005E2F86: cmp dword ptr [esi + 4], 0`
- `005E3055: cmp dword ptr [esi + 4], 0`
- `005E3124: cmp dword ptr [esi + 4], 0`
- `005E31F3: cmp dword ptr [esi + 4], 0`
- `005E32C2: cmp dword ptr [esi + 4], 0`
- `005E3391: cmp dword ptr [esi + 4], 0`
- `005E3460: cmp dword ptr [esi + 4], 0`
- `005E352F: cmp dword ptr [esi + 4], 0`
- `005E35FE: cmp dword ptr [esi + 4], 0`
- `005E36CD: cmp dword ptr [esi + 4], 0`
- `005E392F: and dword ptr [esi], 0`
- `005E398F: and dword ptr [esi], 0`
- `005E39DB: and dword ptr [ebp - 4], 0`
- `005E39E2: cmp dword ptr [edi], 0`
- `005E39FF: and dword ptr [esi], 0`
- `005E3A2C: and dword ptr [ebp - 4], 0`
- `005E3A30: cmp dword ptr [esi + 0x14], 0`
- `005E3A51: and dword ptr [edi], 0`
- `005E3A7E: and dword ptr [ebp - 4], 0`
- `005E3A85: cmp dword ptr [edi], 0`
- `005E3AA2: and dword ptr [esi], 0`
- `005E3ACF: and dword ptr [ebp - 4], 0`
- `005E3AD6: cmp dword ptr [edi], 0`
- `005E3AF3: and dword ptr [esi], 0`
- `005E3B20: and dword ptr [ebp - 4], 0`
- `005E3B27: cmp dword ptr [edi], 0`
- `005E3B44: and dword ptr [esi], 0`
- `005E3B71: and dword ptr [ebp - 4], 0`
- `005E3B75: cmp dword ptr [esi + 0x14], 0`
- `005E3B96: and dword ptr [edi], 0`
- `005E3BC3: and dword ptr [ebp - 4], 0`
- `005E3BCA: cmp dword ptr [edi], 0`
- `005E3BE7: and dword ptr [esi], 0`
- `005E3C14: and dword ptr [ebp - 4], 0`
- `005E3C1B: cmp dword ptr [edi], 0`
- `005E3C38: and dword ptr [esi], 0`
- `005E3C65: and dword ptr [ebp - 4], 0`
- `005E3C6C: cmp dword ptr [edi], 0`
- `005E3C89: and dword ptr [esi], 0`
- `005E3CB6: and dword ptr [ebp - 4], 0`
- `005E3CBD: cmp dword ptr [edi], 0`
- `005E3CDA: and dword ptr [esi], 0`
- `005E3D07: and dword ptr [ebp - 4], 0`
- `005E3D0E: cmp dword ptr [edi], 0`
- `005E3D2B: and dword ptr [esi], 0`
- `005E3D58: and dword ptr [ebp - 4], 0`
- `005E3D5F: cmp dword ptr [edi], 0`
- `005E3D7C: and dword ptr [esi], 0`
- `005E3DA9: and dword ptr [ebp - 4], 0`
- `005E3DB0: cmp dword ptr [edi], 0`
- `005E3DCD: and dword ptr [esi], 0`
- `005E3DFA: and dword ptr [ebp - 4], 0`
- `005E3E01: cmp dword ptr [edi], 0`
- `005E3E1E: and dword ptr [esi], 0`
- `005E3E4B: and dword ptr [ebp - 4], 0`
- `005E3E52: cmp dword ptr [edi], 0`
- `005E3E6F: and dword ptr [esi], 0`
- `005E3E9C: and dword ptr [ebp - 4], 0`
- `005E3EA3: cmp dword ptr [edi], 0`
- `005E3EC0: and dword ptr [esi], 0`
- `005E3EED: and dword ptr [ebp - 4], 0`
- `005E3EF4: cmp dword ptr [edi], 0`
- `005E3F11: and dword ptr [esi], 0`
- `005E3F3E: and dword ptr [ebp - 4], 0`
- `005E3F45: cmp dword ptr [edi], 0`
- `005E3F65: and dword ptr [esi], 0`
- `005E3F92: and dword ptr [ebp - 4], 0`
- `005E3F99: cmp dword ptr [edi], 0`
- `005E3FB9: and dword ptr [esi], 0`
- `005E3FE6: and dword ptr [ebp - 4], 0`
- `005E3FED: cmp dword ptr [edi], 0`
- `005E400A: and dword ptr [esi], 0`
- `005E4037: and dword ptr [ebp - 4], 0`
- `005E403E: cmp dword ptr [edi], 0`
- `005E405B: and dword ptr [esi], 0`
- `005E4088: and dword ptr [ebp - 4], 0`
- `005E408F: cmp dword ptr [edi], 0`
- `005E40AC: and dword ptr [esi], 0`
- `005E40D9: and dword ptr [ebp - 4], 0`
- `005E40E0: cmp dword ptr [edi], 0`
- `005E40FD: and dword ptr [esi], 0`
- `005E412A: and dword ptr [ebp - 4], 0`
- `005E4131: cmp dword ptr [edi], 0`
- `005E414E: and dword ptr [esi], 0`
- `005E417B: and dword ptr [ebp - 4], 0`
- `005E4182: cmp dword ptr [edi], 0`
- `005E419F: and dword ptr [esi], 0`
- `005E41CC: and dword ptr [ebp - 4], 0`
- `005E41D3: cmp dword ptr [edi], 0`
- `005E41F3: and dword ptr [esi], 0`
- `005E4220: and dword ptr [ebp - 4], 0`
- `005E4227: cmp dword ptr [edi], 0`
- `005E4244: and dword ptr [esi], 0`
- `005E4271: and dword ptr [ebp - 4], 0`
- `005E4278: cmp dword ptr [edi], 0`
- `005E4295: and dword ptr [esi], 0`
- `005E42C2: and dword ptr [ebp - 4], 0`
- `005E42C9: cmp dword ptr [edi], 0`
- `005E42E6: and dword ptr [esi], 0`
- `005E4313: and dword ptr [ebp - 4], 0`
- `005E431A: cmp dword ptr [edi], 0`
- `005E4337: and dword ptr [esi], 0`
- `005E4364: and dword ptr [ebp - 4], 0`
- `005E436B: cmp dword ptr [edi], 0`
- `005E4388: and dword ptr [esi], 0`
- `005E43B5: and dword ptr [ebp - 4], 0`
- `005E43BC: cmp dword ptr [edi], 0`
- `005E43D9: and dword ptr [esi], 0`
- `005E43F2: and dword ptr [eax + 4], 0`
- `005E4422: or byte ptr [0xbf6ad0], 1`
- `005E4429: and dword ptr [0xbf6b44], 0`
- `005E5AAB: cmp dword ptr [esi + 4], 0`
- `005E5AB8: and dword ptr [esi + 4], 0`
- `005E5AE8: mov dword ptr [ebp - 4], 1`
- `005E5AF4: and byte ptr [ebp - 4], 0`
- `005E5B7D: and dword ptr [esi], 0`
- `005E5BE9: and dword ptr [esi], 0`
- `005E5C55: and dword ptr [esi], 0`
- `005E5CC1: and dword ptr [esi], 0`
- `005E5D2D: and dword ptr [esi], 0`
- `005E5D4C: cmp dword ptr [ebp + 0x14], 0`
- `005E5E39: cmp dword ptr [ebp + 0x14], 0`
- `005E5F75: and dword ptr [esi], 0`
- `005E5F97: and dword ptr [esi + 0x14], 0`
- `005E5FEB: and dword ptr [esi + 0x14], 0`
- `005E6099: and dword ptr [ebp - 4], 0`
- `005E60A7: mov byte ptr [ebp - 4], 1`
- `005E610F: and dword ptr [esi + 0x14], 0`
- `005E6163: and dword ptr [esi + 0x14], 0`
- `005E6275: cmp dword ptr [edi + 0x14], 0`
- `005E627C: mov dword ptr [ebp - 4], 1`
- `005E628E: and dword ptr [esi + 4], 0`
- `005E62D0: cmp dword ptr [edi + 0x14], 0`
- `005E62D7: mov dword ptr [ebp - 4], 1`
- `005E62E9: and dword ptr [esi + 4], 0`
- `005E6345: mov dword ptr [ebp - 4], 1`
- `005E6387: cmp dword ptr [edi + 0x14], 0`
- `005E638E: mov dword ptr [ebp - 4], 1`
- `005E63A0: and dword ptr [esi + 4], 0`
- `005E63E4: mov dword ptr [ebp - 4], 1`
- `005E6654: and dword ptr [ebp - 4], 0`
- `005E665B: cmp dword ptr [edi], 0`
- `005E6678: and dword ptr [esi], 0`
- `005E66A5: and dword ptr [ebp - 4], 0`
- `005E66AC: cmp dword ptr [edi], 0`
- `005E66C9: and dword ptr [esi], 0`
- `005E66F6: and dword ptr [ebp - 4], 0`
- `005E66FD: cmp dword ptr [edi], 0`
- `005E671A: and dword ptr [esi], 0`
- `005E6747: and dword ptr [ebp - 4], 0`
- `005E674E: cmp dword ptr [edi], 0`
- `005E676E: and dword ptr [esi], 0`
- `005E679B: and dword ptr [ebp - 4], 0`
- `005E67A2: cmp dword ptr [edi], 0`
- `005E67BF: and dword ptr [esi], 0`
- `005E67EC: and dword ptr [ebp - 4], 0`
- `005E67F3: cmp dword ptr [edi], 0`
- `005E6810: and dword ptr [esi], 0`
- `005E6AAC: mov byte ptr [ebp - 4], 1`
- `005E6ABC: mov byte ptr [ebp - 4], 1`
- `005E6AD5: mov byte ptr [ebp - 4], 3`
- `005E6B27: mov byte ptr [ebp - 4], 6`
- `005E6B42: mov byte ptr [ebp - 4], 5`
- `005E6EDF: mov byte ptr [ebp - 4], 5`
- `005E6F1D: mov byte ptr [ebp - 4], 5`
- `005E6F93: mov byte ptr [ebp - 4], 1`
- `005E6FA0: mov byte ptr [ebp - 4], 1`
- `005E6FB9: mov byte ptr [ebp - 4], 3`
- `005E7007: mov byte ptr [ebp - 4], 6`
- `005E701F: mov byte ptr [ebp - 4], 5`
- `005E725B: mov byte ptr [ebp - 4], 5`
- `005E72D1: mov byte ptr [ebp - 4], 1`
- `005E72E1: mov byte ptr [ebp - 4], 1`
- `005E72FA: mov byte ptr [ebp - 4], 3`
- `005E7349: mov byte ptr [ebp - 4], 6`
- `005E7361: mov byte ptr [ebp - 4], 5`
- `005E7658: mov byte ptr [ebp - 4], 5`
- `005E76CD: mov byte ptr [ebp - 4], 1`
- `005E76DD: mov byte ptr [ebp - 4], 1`
- `005E76F6: mov byte ptr [ebp - 4], 3`
- `005E7747: mov byte ptr [ebp - 4], 6`
- `005E775F: mov byte ptr [ebp - 4], 5`
- `005E79E6: mov byte ptr [ebp - 4], 5`
- `005E7A48: mov byte ptr [ebp - 4], 1`
- `005E7A58: mov byte ptr [ebp - 4], 1`
- `005E7A69: mov byte ptr [ebp - 4], 3`
- `005E7A85: mov byte ptr [ebp - 4], 1`
- `005E7AB1: mov byte ptr [ebp - 4], 1`
- `005E7AC2: mov byte ptr [ebp - 4], 5`
- `005E7ADD: mov byte ptr [ebp - 4], 1`
- `005E7B09: mov byte ptr [ebp - 4], 1`
- `005E7B36: mov byte ptr [ebp - 4], 1`
- `005E7B62: mov byte ptr [ebp - 4], 1`
- `005E7B8F: mov byte ptr [ebp - 4], 1`
- `005E7BBB: mov byte ptr [ebp - 4], 1`
- `005E7BE8: mov byte ptr [ebp - 4], 1`
- `005E7C14: mov byte ptr [ebp - 4], 1`
- `005E7C41: mov byte ptr [ebp - 4], 1`
- `005E7C6D: mov byte ptr [ebp - 4], 1`
- `005E7C9A: mov byte ptr [ebp - 4], 1`
- `005E7CC6: mov byte ptr [ebp - 4], 1`
- `005E7CF3: mov byte ptr [ebp - 4], 1`
- `005E7D1F: mov byte ptr [ebp - 4], 1`
- `005E7D4C: mov byte ptr [ebp - 4], 1`
- `005E7D7C: mov byte ptr [ebp - 4], 1`
- `005E8422: mov byte ptr [ebp - 4], 1`
- `005E8528: mov byte ptr [ebp - 4], 1`
- `005E85B5: mov byte ptr [ebp - 4], 2`
- `005E860C: mov byte ptr [ebp - 4], 4`
- `005E8663: mov byte ptr [ebp - 4], 6`
- `005E8C4E: cmp dword ptr [esi + 4], 0`
- `005E8C5B: and dword ptr [esi + 4], 0`
- `005E8C68: cmp dword ptr [esi + 4], 0`
- `005E8C75: and dword ptr [esi + 4], 0`
- `005E8C81: mov dword ptr [eax + 4], 1`
- `005E8CB8: cmp dword ptr [esi + 4], 0`
- `005E8CC5: and dword ptr [esi + 4], 0`
- `005E8DB7: cmp dword ptr [esi + 4], 0`
- `005E8E0F: cmp dword ptr [esi + 4], 0`
- `005E8E8F: and dword ptr [eax + 0x10], 0`
- `005E8E9D: cmp dword ptr [ebp + 0xc], 0`
- `005E8EB4: cmp dword ptr [ebp + 0xc], 0`
- `005E8F37: and dword ptr [edi + 4], 0`
- `005E8F3B: and dword ptr [edi + 0xc], 0`
- `005E8F46: cmp dword ptr [esi + 4], 0`
- `005E8F81: cmp dword ptr [esp + 0x10], 0`
- `005E8FAA: cmp dword ptr [esi + 4], 0`
- `005E9046: cmp dword ptr [ebp + 0xc], 0`
- `005E90F1: and dword ptr [edi + 4], 0`
- `005E90F5: and dword ptr [edi + 0xc], 0`
- `005E9100: cmp dword ptr [esi + 4], 0`
- `005E9157: cmp dword ptr [esi + 4], 0`
- `005E91D1: and dword ptr [eax + 0xc], 0`
- `005E91D5: and dword ptr [eax + 0x10], 0`
- `005E927A: and dword ptr [edi + 4], 0`
- `005E927E: and dword ptr [edi + 0xc], 0`
- `005E92F0: and dword ptr [esi + 0x10], 0`
- `005E92F4: and dword ptr [esi + 0xc], 0`
- `005E92F8: and dword ptr [esi + 8], 0`
- `005E931D: and dword ptr [esi], 0`
- `005E9344: and dword ptr [esi], 0`
- `005E936B: and dword ptr [esi], 0`
- `005E93D7: and dword ptr [esi], 0`
- `005EA03B: and dword ptr [ebp - 4], 0`
- `005EA049: mov byte ptr [ebp - 4], 1`
- `005EA18B: and dword ptr [esi + 0x10], 0`
- `005EA18F: and dword ptr [esi + 0xc], 0`
- `005EA193: and dword ptr [esi + 8], 0`
- `005EA1C5: and dword ptr [esi + 0x10], 0`
- `005EA1C9: and dword ptr [esi + 0xc], 0`
- `005EA1CD: and dword ptr [esi + 8], 0`
- `005EA1FF: and dword ptr [esi + 0x10], 0`
- `005EA203: and dword ptr [esi + 0xc], 0`
- `005EA207: and dword ptr [esi + 8], 0`
- `005EA221: mov dword ptr [ebp - 4], 1`
- `005EA265: mov dword ptr [ebp - 4], 1`
- `005EA277: and byte ptr [ebp - 4], 0`
- `005EA2CD: cmp dword ptr [esi + 4], 0`
- `005EA2DC: and dword ptr [esi + 4], 0`
- `005EA362: and dword ptr [ebp - 4], 0`
- `005EA366: cmp dword ptr [edi + 0x10], 0`
- `005EA378: and dword ptr [esi + 4], 0`
- `005EA3A8: and dword ptr [ebp - 4], 0`
- `005EA4AC: cmp dword ptr [esi + 4], 0`
- `005EA557: cmp dword ptr [esi + 4], 0`
- `005EA602: cmp dword ptr [esi + 4], 0`
- `005EA6F4: and dword ptr [ebp - 4], 0`
- `005EA6FB: cmp dword ptr [edi], 0`
- `005EA718: and dword ptr [esi], 0`
- `005EA745: and dword ptr [ebp - 4], 0`
- `005EA74C: cmp dword ptr [edi], 0`
- `005EA769: and dword ptr [esi], 0`
- `005EA796: and dword ptr [ebp - 4], 0`
- `005EA79D: cmp dword ptr [edi], 0`
- `005EA7BA: and dword ptr [esi], 0`
- `005EA7E7: and dword ptr [ebp - 4], 0`
- `005EA7EE: cmp dword ptr [edi], 0`
- `005EA80B: and dword ptr [esi], 0`
- `005EAD8C: and dword ptr [esi], 0`
- `005EADF8: and dword ptr [esi], 0`
- `005EAE64: and dword ptr [esi], 0`
- `005EAF3C: and dword ptr [esi], 0`
- `005EAF5E: and dword ptr [esi + 0x10], 0`
- `005EAF62: and dword ptr [esi + 0x14], 0`
- `005EAFB6: and dword ptr [esi + 0x10], 0`
- `005EAFBA: and dword ptr [esi + 0x14], 0`
- `005EB00E: and dword ptr [esi + 0x10], 0`
- `005EB012: and dword ptr [esi + 0x14], 0`
- `005EB016: and dword ptr [esi + 0x18], 0`
- `005EB06A: and dword ptr [esi + 0x10], 0`
- `005EB06E: and dword ptr [esi + 0x14], 0`
- `005EB072: and dword ptr [esi + 0x18], 0`
- `005EB1AC: and dword ptr [ebp - 4], 0`
- `005EB1B3: cmp dword ptr [edi], 0`
- `005EB1D0: and dword ptr [esi], 0`
- `005EB1FD: and dword ptr [ebp - 4], 0`
- `005EB204: cmp dword ptr [edi], 0`
- `005EB221: and dword ptr [esi], 0`
- `005EB24E: and dword ptr [ebp - 4], 0`
- `005EB255: cmp dword ptr [edi], 0`
- `005EB272: and dword ptr [esi], 0`
- `005EB29F: and dword ptr [ebp - 4], 0`
- `005EB2A6: cmp dword ptr [edi], 0`
- `005EB2C3: and dword ptr [esi], 0`
- `005EB3B6: mov byte ptr [ebp - 4], 1`
- `005EB52B: mov byte ptr [ebp - 4], 6`
- `005EB53A: mov byte ptr [ebp - 4], 5`
- `005EB549: mov byte ptr [ebp - 4], 4`
- `005EB558: mov byte ptr [ebp - 4], 3`
- `005EB567: mov byte ptr [ebp - 4], 2`
- `005EB576: mov byte ptr [ebp - 4], 1`
- `005EB57F: and byte ptr [ebp - 4], 0`
- `005EB583: cmp dword ptr [esi + 0x8c], 0`
- `005EB59B: and dword ptr [edi + 4], 0`
- `005EB5FB: mov byte ptr [ebp - 4], 1`
- `005EB60C: and byte ptr [ebp - 4], 0`
- `005EB642: mov dword ptr [ebp - 0x78], 2`
- `005EB662: mov dword ptr [ebp - 0x34], 1`
- `005EB678: mov byte ptr [ebp - 4], 2`
- `005EB68C: mov byte ptr [ebp - 4], 3`
- `005EB69A: mov byte ptr [ebp - 4], 2`
- `005EB6BB: mov byte ptr [ebp - 4], 4`
- `005EB6D3: mov byte ptr [ebp - 4], 2`
- `005EB714: mov byte ptr [ebp - 4], 5`
- `005EB722: mov byte ptr [ebp - 4], 2`
- `005EB743: mov byte ptr [ebp - 4], 6`
- `005EB75B: mov byte ptr [ebp - 4], 2`
- `005EB92F: cmp dword ptr [ebx + 0x5d4], 0`
- `005EBAFE: cmp dword ptr [ebx + 0x5d8], 0`
- `005EBB70: cmp dword ptr [ebx + 0x5d8], 0`
- `005EBBB5: mov byte ptr [ebp - 4], 2`
- `005EBBBE: and byte ptr [ebp - 4], 0`
- `005EBBF2: cmp dword ptr [ecx + 0x90], 0`
- `005EBCBF: and dword ptr [esi], 0`
- `005EBCE2: cmp dword ptr [esp + 4], 1`
- `005EBCFB: cmp dword ptr [esp + 8], 2`
- `005EBD9C: and dword ptr [ebp - 4], 0`
- `005EBDDA: mov dword ptr [ebp - 4], 1`
- `005EBE38: mov dword ptr [ebp - 4], 2`
- `005EBEA2: mov dword ptr [ebp - 4], 3`
- `005EBEBD: mov byte ptr [ebp - 4], 4`
- `005EBECE: mov byte ptr [ebp - 4], 3`
- `005EBEF0: mov byte ptr [ebp - 4], 5`
- `005EBEFE: mov byte ptr [ebp - 4], 6`
- `005EBF4F: mov byte ptr [ebp - 4], 5`
- `005EBF67: mov byte ptr [ebp - 4], 3`
- `005EBFEE: mov byte ptr [ebp - 4], 3`
- `005EC0F8: mov byte ptr [ebp - 4], 3`
- `005EC450: cmp dword ptr [esi + 0x5d4], 0`
- `005EC470: cmp dword ptr [esi + 0x5d4], 0`
- `005EC5A5: mov dword ptr [ebp - 4], 1`
- `005EC673: mov byte ptr [ebp - 4], 2`
- `005EC681: mov byte ptr [ebp - 4], 1`
- `005EC6B1: and dword ptr [0xbed9dc], 0`
- `005ED3ED: or byte ptr [0xbf6ad0], 1`
- `005ED3F4: and dword ptr [0xbf6b44], 0`
- `005EDB19: mov byte ptr [ebp - 4], 2`
- `005EDB2F: mov byte ptr [ebp - 4], 3`
- `005EDB48: mov byte ptr [ebp - 4], 3`
- `005EDB61: mov byte ptr [ebp - 4], 5`
- `005EDD1B: mov byte ptr [ebp - 4], 1`
- `005EDD97: mov byte ptr [ebp - 4], 1`
- `005EDDDD: mov byte ptr [ebp - 4], 2`
- `005EDE00: mov byte ptr [ebp - 4], 2`
- `005EDE14: mov byte ptr [ebp - 4], 1`
- `005EDE70: mov byte ptr [ebp - 4], 1`
- `005EDE86: mov byte ptr [ebp - 4], 2`
- `005EDE9A: mov byte ptr [ebp - 4], 1`
- `005EDEC9: mov byte ptr [ebp - 4], 3`
- `005EDED5: mov byte ptr [ebp - 4], 1`
- `005EDEEE: and byte ptr [ebp - 4], 0`
- `005EDF2A: cmp dword ptr [ecx + 0x18], 0`
- `005EDF82: mov byte ptr [ebp - 4], 1`
- `005EDF98: mov byte ptr [ebp - 4], 2`
- `005EDFB6: mov byte ptr [ebp + 0xb], 1`
- `005EDFBF: mov byte ptr [ebp - 4], 1`
- `005EDFCF: cmp byte ptr [ebp + 0xb], 0`
- `005EDFD5: and byte ptr [ebp - 4], 0`
- `005EE02A: mov byte ptr [ebp - 4], 3`
- `005EE10B: mov byte ptr [ebp - 4], 4`
- `005EE116: mov byte ptr [ebp - 4], 5`
- `005EE15F: mov byte ptr [ebp - 4], 4`
- `005EE177: mov byte ptr [ebp - 4], 3`
- `005EE1B1: mov byte ptr [ebp - 4], 3`
- `005EE1D7: mov byte ptr [ebp - 4], 3`
- `005EE1F7: mov byte ptr [ebp - 4], 1`
- `005EE20C: and byte ptr [ebp - 4], 0`
- `005EE246: cmp dword ptr [esi + 4], 0`
- `005EE253: and dword ptr [esi + 4], 0`
- `005EE282: cmp dword ptr [esi + 4], 0`
- `005EE28F: and dword ptr [esi + 4], 0`
- `005EE29B: mov dword ptr [eax + 4], 1`
- `005EE2B5: cmp dword ptr [esi + 4], 0`
- `005EE2C2: and dword ptr [esi + 4], 0`
- `005EE2FA: cmp dword ptr [esi + 4], 0`
- `005EE35A: cmp dword ptr [esi + 4], 0`
- `005EE3CB: cmp dword ptr [ebp + 0xc], 0`
- `005EE40D: mov byte ptr [ebp - 4], 1`
- `005EE4CC: and dword ptr [edi + 4], 0`
- `005EE4D0: and dword ptr [edi + 0xc], 0`
- `005EE4ED: and dword ptr [eax], 0`
- `005EE511: cmp dword ptr [ecx], 0`
- `005EE543: cmp dword ptr [esi + 4], 0`
- `005EE5C3: and dword ptr [eax + 0xc], 0`
- `005EE63B: and dword ptr [eax], 0`
- `005EE662: cmp dword ptr [ecx], 0`
- `005EE6AB: and dword ptr [esi], 0`
- `005EE6D2: and dword ptr [esi], 0`
- `005EE73E: and dword ptr [esi], 0`
- `005EF398: and dword ptr [esi + 0x14], 0`
- `005EF39C: and dword ptr [esi + 0x1c], 0`
- `005EF45D: and dword ptr [edi + 4], 0`
- `005EF461: and dword ptr [edi + 0xc], 0`
- `005EF49E: mov dword ptr [ebp - 4], 1`
- `005EF4EA: cmp dword ptr [esi + 4], 0`
- `005EF4F9: and dword ptr [esi + 4], 0`
- `005EF59E: cmp dword ptr [edi + 0x10], 0`
- `005EF5A5: mov dword ptr [ebp - 4], 1`
- `005EF5B7: and dword ptr [esi + 4], 0`
- `005EF5BB: and byte ptr [ebp - 4], 0`
- `005EF5EF: and dword ptr [ebp - 4], 0`
- `005EF656: cmp dword ptr [esi + 4], 0`
- `005EF721: cmp dword ptr [esi + 4], 0`
- `005EF7F8: and dword ptr [ebp - 4], 0`
- `005EF7FF: cmp dword ptr [edi], 0`
- `005EF81C: and dword ptr [esi], 0`
- `005EF849: and dword ptr [ebp - 4], 0`
- `005EF84D: cmp dword ptr [esi + 0x14], 0`
- `005EF86E: and dword ptr [edi], 0`
- `005EF89B: and dword ptr [ebp - 4], 0`
- `005EF8A2: cmp dword ptr [edi], 0`
- `005EF8BF: and dword ptr [esi], 0`
- `005F01FF: and dword ptr [ebp - 4], 0`
- `005F021D: mov byte ptr [ebp - 4], 1`
- `005F0300: mov dword ptr [ebp - 4], 1`
- `005F030C: and byte ptr [ebp - 4], 0`
- `005F0385: mov dword ptr [ebp - 0x5c], 2`
- `005F03F2: mov byte ptr [ebp - 4], 2`
- `005F041C: mov byte ptr [ebp - 4], 3`
- `005F0429: mov byte ptr [ebp - 4], 4`
- `005F0437: mov byte ptr [ebp - 4], 3`
- `005F044C: mov byte ptr [ebp - 4], 2`
- `005F046E: mov byte ptr [ebp - 4], 5`
- `005F0486: mov byte ptr [ebp - 4], 6`
- `005F0497: mov byte ptr [ebp - 4], 5`
- `005F05CD: cmp byte ptr [eax], 0`
- `005F0968: cmp dword ptr [ebp + 0x1c], 0`
- `005F0981: cmp dword ptr [ebp + 0x24], 0`
- `005F09A6: cmp dword ptr [ebp + 0x18], 0`
- `005F09B5: cmp dword ptr [ebp + 0x18], 0`
- `005F09DD: cmp dword ptr [ebp + 0x18], 0`
- `005F09E9: cmp dword ptr [ebp + 0x1c], 0`
- `005F09F5: cmp dword ptr [ebp + 0x24], 0`
- `005F0A3E: cmp dword ptr [ebp + 0x18], 0`
- `005F0A4D: cmp dword ptr [ebp + 0x18], 0`
- `005F0A59: cmp dword ptr [ebp + 0x1c], 0`
- `005F0A7B: cmp dword ptr [ebp + 0x24], 0`
- `005F0B8A: and dword ptr [ebp + 0x28], 0`
- `005F0B8E: cmp dword ptr [ebp - 0x20], 0`
- `005F0BA5: cmp dword ptr [ebp + 0x1c], 0`
- `005F0BB9: cmp dword ptr [ebp - 0x10], 0`
- `005F0C26: cmp dword ptr [ebp + 0x1c], 0`
- `005F0C5B: cmp dword ptr [ebp + 0x24], 0`
- `005F0C6F: cmp dword ptr [ebp - 0x10], 0`
- `005F0CE5: cmp dword ptr [ebp + 0x18], 0`
- `005F0CF9: cmp dword ptr [ebp - 0x10], 0`
- `005F0EE7: cmp dword ptr [ebp + 0x18], 1`
- `005F13D9: cmp dword ptr [ebp - 0x10], 0`
- `005F1522: cmp dword ptr [ebp - 0x48], 0`
- `005F1574: cmp dword ptr [ebp - 0x10], 0`
- `005F1644: cmp dword ptr [ebp - 0x10], 0`
- `005F167C: cmp dword ptr [ebp - 0x10], 0`
- `005F17A5: cmp dword ptr [ebx], 0`
- `005F17DE: cmp dword ptr [ebx], 0`
- `005F1832: cmp dword ptr [ebx], 0`
- `005F18A6: cmp dword ptr [ebx], 0`
- `005F19B7: cmp dword ptr [eax + esi*4 + 0x7c], 0`
- `005F19F1: cmp dword ptr [esi], 0`
- `005F1A56: cmp dword ptr [ebx], 0`
- `005F1AE7: cmp dword ptr [ebp - 0x10], 0`
- `005F1B2B: mov byte ptr [ebp - 4], 2`
- `005F1B3A: mov byte ptr [ebp - 4], 1`
- `005F1B46: and byte ptr [ebp - 4], 0`
- `005F1BBF: and dword ptr [0xbed9e8], 0`
- `005F2D7F: or byte ptr [0xbf6ad0], 1`
- `005F2D86: and dword ptr [0xbf6b44], 0`
- `005F3F72: cmp dword ptr [esi + 0x1cc], 0`
- `005F3F8E: and dword ptr [edi + 4], 0`
- `005F4037: mov byte ptr [ebp - 4], 5`
- `005F4046: mov byte ptr [ebp - 4], 4`
- `005F4055: mov byte ptr [ebp - 4], 3`
- `005F4064: mov byte ptr [ebp - 4], 2`
- `005F4073: mov byte ptr [ebp - 4], 1`
- `005F407C: and byte ptr [ebp - 4], 0`
- `005F4325: mov byte ptr [ebp - 4], 1`
- `005F4339: mov byte ptr [ebp - 4], 1`
- `005F4352: mov byte ptr [ebp - 4], 3`
- `005F437F: mov byte ptr [ebp - 4], 1`
- `005F4393: and byte ptr [ebp - 4], 0`
- `005F43F6: mov dword ptr [ebp - 4], 5`
- `005F4485: mov dword ptr [ebp - 4], 6`
- `005F47E9: cmp dword ptr [ebx + 0x164], 0`
- `005F4876: cmp dword ptr [ebx + 0x164], 0`
- `005F48B1: cmp dword ptr [eax + 0x24], 1`
- `005F4AE4: cmp dword ptr [0xbf14ec], 0`
- `005F4B0C: cmp dword ptr [esi], 0`
- `005F4C6F: cmp dword ptr [eax + 0x24], 1`
- `005F4D48: mov byte ptr [ebp - 4], 1`
- `005F4E8B: mov dword ptr [ebp - 4], 6`
- `005F4EC6: mov dword ptr [ebp - 4], 5`
- `005F4FB8: mov dword ptr [ebp - 4], 4`
- `005F5046: mov dword ptr [ebp - 4], 3`
- `005F50D4: mov dword ptr [ebp - 4], 2`
- `005F512C: cmp dword ptr [esi + 0x168], 4`
- `005F514E: cmp dword ptr [esi + 0x168], 2`
- `005F51CD: cmp dword ptr [esi + 0x168], 5`
- `005F542D: cmp dword ptr [esi + 0x168], 3`
- `005F54C3: cmp dword ptr [ebp - 0x10], 3`
- `005F54D6: cmp dword ptr [esi + 0x168], 3`
- `005F5557: mov dword ptr [ebp - 4], 3`
- `005F5603: mov byte ptr [ebp - 4], 5`
- `005F560F: mov byte ptr [ebp - 4], 4`
- `005F5643: cmp dword ptr [ebp - 0x10], 2`
- `005F566E: mov dword ptr [ebp - 4], 2`
- `005F569D: mov dword ptr [esi + 0x214], 1`
- `005F5747: cmp dword ptr [esi + 0x180], 1`
- `005F57A9: mov dword ptr [ebp - 4], 1`
- `005F57C1: cmp dword ptr [ebp - 0x10], 5`
- `005F5814: cmp dword ptr [eax + 0x24], 2`
- `005F5840: cmp dword ptr [ebp - 0x10], 5`
- `005F5855: cmp dword ptr [esi + 0x168], 5`
- `005F5C15: mov dword ptr [ebp - 4], 5`
- `005F5C59: mov dword ptr [ebp - 4], 6`
- `005F5C8E: mov dword ptr [eax + 0x23c], 1`
- `005F5DD4: cmp dword ptr [ebx], 0`
- `005F5E83: cmp dword ptr [ebx + 0x1f0], 0`
- `005F5E9D: mov dword ptr [ebp - 4], 4`
- `005F607E: cmp dword ptr [eax + 0x1f0], 0`
- `005F64BA: cmp dword ptr [ebx + 0x168], 5`
- `005F651E: mov byte ptr [ebp - 4], 1`
- `005F6531: mov byte ptr [ebp - 4], 3`
- `005F6585: mov dword ptr [ebp - 4], 4`
- `005F6591: cmp dword ptr [esi], 0`
- `005F6594: mov byte ptr [ebp - 4], 5`
- `005F65E4: mov byte ptr [ebp - 4], 4`
- `005F662F: mov dword ptr [ebp - 4], 6`
- `005F685F: cmp dword ptr [ebx], 0`
- `005F6920: and dword ptr [ecx + 0x238], 0`
- `005F6927: mov dword ptr [ecx + 0x23c], 1`
- `005F6944: mov dword ptr [esi + 0x170], 1`
- `005F6B1A: mov dword ptr [ebp - 4], 1`
- `005F6B68: mov dword ptr [ebp - 4], 2`
- `005F6B8A: mov byte ptr [ebp - 4], 3`
- `005F6C4B: mov byte ptr [ebp - 4], 2`
- `005F6D5C: cmp dword ptr [ecx], 0`
- `005F6E3D: mov byte ptr [ebp - 4], 1`
- `005F6EAD: mov byte ptr [ebp - 4], 2`
- `005F6EF3: mov byte ptr [ebp - 4], 5`
- `005F6F0B: mov byte ptr [ebp - 4], 6`
- `005F6F17: and dword ptr [ecx], 0`
- `005F6F6A: mov byte ptr [ebp - 4], 5`
- `005F6FF2: mov byte ptr [ebp - 4], 1`
- `005F6FFB: and byte ptr [ebp - 4], 0`
- `005F7133: mov byte ptr [ebp - 4], 3`
- `005F713E: mov byte ptr [ebp - 4], 2`
- `005F716D: mov byte ptr [ebp - 4], 4`
- `005F7178: mov byte ptr [ebp - 4], 2`
- `005F71A6: and dword ptr [eax + 0x170], 0`
- `005F71B0: mov byte ptr [ebp - 4], 1`
- `005F71B9: and byte ptr [ebp - 4], 0`
- `005F73D4: mov dword ptr [ebp - 4], 4`
- `005F7418: mov dword ptr [ebp - 4], 5`
- `005F745A: mov byte ptr [ebp - 4], 6`
- `005F7531: mov byte ptr [ebp - 4], 6`
- `005F753A: mov byte ptr [ebp - 4], 5`
- `005F759C: mov byte ptr [ebp - 4], 1`
- `005F75C9: mov byte ptr [ebp - 4], 2`
- `005F75FF: mov byte ptr [ebp - 4], 3`
- `005F764C: mov byte ptr [ebp - 4], 2`
- `005F7658: mov byte ptr [ebp - 4], 1`
- `005F7678: mov dword ptr [edi + 0x170], 1`
- `005F769E: and dword ptr [ebp - 4], 0`
- `005F77B4: mov byte ptr [ebp - 4], 1`
- `005F790D: mov byte ptr [ebp - 4], 1`
- `005F792F: mov byte ptr [ebp - 4], 6`
- `005F795E: mov byte ptr [ebp - 4], 1`
- `005F7994: mov byte ptr [ebp - 4], 1`
- `005F7ACE: mov byte ptr [ebp - 4], 1`
- `005F7AF8: mov byte ptr [ebp - 4], 2`
- `005F7B0B: mov byte ptr [ebp - 4], 1`
- `005F7B28: mov byte ptr [ebp - 4], 3`
- `005F7B6A: mov byte ptr [ebp - 4], 4`
- `005F7BA0: mov byte ptr [ebp - 4], 5`
- `005F7BED: mov byte ptr [ebp - 4], 4`
- `005F7BF9: mov byte ptr [ebp - 4], 3`
- `005F7C05: mov byte ptr [ebp - 4], 2`
- `005F7C0E: mov byte ptr [ebp - 4], 1`
- `005F7C31: mov dword ptr [esi + 0x170], 1`
- `005F7D41: mov byte ptr [ebp - 4], 2`
- `005F7DD9: mov byte ptr [ebp - 4], 3`
- `005F7E4B: mov byte ptr [ebp - 4], 2`
- `005F7F64: and dword ptr [ebp - 4], 0`
- `005F7F6C: and dword ptr [esi], 0`
- `005F7F8F: and dword ptr [ebp - 0x10], 0`
- `005F7F99: and dword ptr [ebp - 4], 0`
- `005F7FF7: cmp dword ptr [esi + 0x170], 0`
- `005F8035: and dword ptr [ebp - 4], 0`
- `005F803C: and dword ptr [ecx], 0`
- `005F8089: cmp dword ptr [edi + 0x170], 0`
- `005F80AE: and dword ptr [ebp - 4], 0`
- `005F80E0: mov dword ptr [edi + 0x170], 1`
- `005F82F7: cmp dword ptr [esi + 0x168], 1`
- `005F834F: cmp dword ptr [edi + 0x168], 1`
- `005F839E: and dword ptr [ebp - 4], 0`
- `005F83CD: mov dword ptr [edi + 0x20c], 1`
- `005F8443: cmp dword ptr [ebp - 0x1c], 2`
- `005F8513: mov byte ptr [ebp - 4], 1`
- `005F8574: mov byte ptr [ebp - 4], 2`
- `005F859E: mov byte ptr [ebp - 4], 3`
- `005F85EF: mov byte ptr [ebp - 4], 4`
- `005F860E: mov byte ptr [ebp - 4], 5`
- `005F8625: mov byte ptr [ebp - 4], 5`
- `005F8CE8: cmp dword ptr [eax + 0x24], 1`
- `005F8DEA: mov dword ptr [ebp - 4], 1`
- `005F8E5E: cmp byte ptr [eax], 0`
- `005F8E7D: and dword ptr [ecx], 0`
- `005F8E89: mov byte ptr [ebp - 4], 1`
- `005F8E99: and byte ptr [ebp - 4], 0`
- `005F8ED2: and dword ptr [ebp - 4], 0`
- `005F8EDA: cmp byte ptr [eax], 0`
- `005F8EEA: and dword ptr [esi + 0x90], 0`
- `005F8F02: mov dword ptr [esi + 0x90], 1`
- `005F903F: mov dword ptr [ebp - 4], 1`
- `005F90FF: mov dword ptr [ebp - 4], 2`
- `005F9161: mov dword ptr [ebp - 4], 3`
- `005F91CE: mov byte ptr [ebp - 4], 4`
- `005F91F8: mov byte ptr [ebp - 4], 5`
- `005F920F: mov byte ptr [ebp - 4], 4`
- `005F924F: mov byte ptr [ebp - 4], 3`
- `005F93C7: mov dword ptr [ebp - 4], 1`
- `005F9438: mov dword ptr [eax + 0x184], 1`
- `005F94AF: mov dword ptr [ebp - 4], 2`
- `005F953D: mov byte ptr [ebp - 4], 3`
- `005F9553: mov byte ptr [ebp - 4], 2`
- `005F95F9: and dword ptr [ebp - 4], 0`
- `005F9645: mov dword ptr [ebp - 4], 1`
- `005F9682: mov dword ptr [ebp - 4], 2`
- `005F96FB: mov dword ptr [ebp - 4], 3`
- `005F977D: and dword ptr [ebp - 0x18], 0`
- `005F9783: mov dword ptr [ebp - 4], 4`
- `005F97B1: mov byte ptr [ebp - 4], 5`
- `005F97BD: mov byte ptr [ebp - 4], 4`
- `005F9810: cmp dword ptr [0xbeda54], 0`
- `005F9833: and dword ptr [ebp - 4], 0`
- `005F9845: cmp dword ptr [0xbeda4c], 0`
- `005F9861: mov dword ptr [ebp - 4], 1`
- `005F99B1: mov dword ptr [ebp - 4], 1`
- `005F9B67: mov dword ptr [ebp - 4], 2`
- `005F9B8D: mov dword ptr [ebp - 4], 3`
- `005F9BB7: cmp dword ptr [eax + 0x24], 1`
- `005F9BBD: cmp byte ptr [esi + 0x174], 0`
- `005F9BD5: mov dword ptr [ebp - 4], 4`
- `005F9CAD: mov byte ptr [ebp - 4], 1`
- `005F9E99: and dword ptr [eax + 0x2568], 0`
- `005F9F7C: and dword ptr [ebp - 4], 0`
- `005F9F9B: and dword ptr [0xbeda2c], 0`
- `005FA355: and dword ptr [ecx + eax*4], 0`
- `005FA381: cmp byte ptr [eax], 0`
- `005FA3B8: cmp dword ptr [0xbeda4c], 0`
- `005FA3D5: and dword ptr [ebp - 4], 0`
- `005FA498: and dword ptr [ebp - 4], 0`
- `005FA514: and dword ptr [ebp - 4], 0`
- `005FA535: and dword ptr [esi + 0x88], 0`
- `005FA53C: and dword ptr [esi + 0x8c], 0`
- `005FA54C: mov byte ptr [ebp - 4], 3`
- `005FA579: mov byte ptr [ebp - 4], 4`
- `005FA585: mov byte ptr [ebp - 4], 3`
- `005FA5B5: mov dword ptr [ebp - 0x24], 1`
- `005FA5DE: mov byte ptr [ebp - 4], 1`
- `005FA608: mov byte ptr [ebp - 4], 2`
- `005FA6AE: mov byte ptr [ebp - 4], 1`
- `005FA6EC: and byte ptr [ebp - 4], 0`
- `005FA729: mov dword ptr [ebp - 4], 2`
- `005FA74B: mov byte ptr [ebp - 4], 3`
- `005FA75F: mov byte ptr [ebp - 4], 3`
- `005FA778: mov byte ptr [ebp - 4], 5`
- `005FA7A0: mov byte ptr [ebp - 4], 6`
- `005FA7C1: mov byte ptr [ebp - 4], 5`
- `005FA7E2: mov byte ptr [ebp - 4], 3`
- `005FA7FA: mov byte ptr [ebp - 4], 2`
- `005FA8C5: cmp dword ptr [ebx], 0`
- `005FA928: cmp dword ptr [ebx], 0`
- `005FA972: cmp dword ptr [ebx], 0`
- `005FAA12: cmp dword ptr [ebx], 0`
- `005FAA32: cmp dword ptr [esi], 0`
- `005FAADA: cmp dword ptr [ebx], 0`
- `005FABD7: and dword ptr [ebp - 4], 0`
- `005FABEE: mov byte ptr [ebp - 4], 2`
- `005FABFD: mov byte ptr [ebp - 4], 1`
- `005FAC06: and dword ptr [0xbeda74], 0`
- `005FAC60: and dword ptr [ebp - 4], 0`
- `005FAEE2: mov dword ptr [ebp - 4], 2`
- `005FAEF1: mov byte ptr [ebp - 4], 3`
- `005FAF3A: mov dword ptr [ebp - 4], 4`
- `005FB04D: mov dword ptr [ebp - 4], 5`
- `005FB05C: mov byte ptr [ebp - 4], 6`
- `005FB0F7: and dword ptr [esi + 0x11c], 0`
- `005FB109: mov dword ptr [esi + 0x120], 1`
- `005FB118: and dword ptr [ebp - 4], 0`
- `005FB1F9: mov dword ptr [ebp - 4], 1`
- `005FB337: mov dword ptr [ebp - 4], 1`
- `005FB4BD: mov dword ptr [ebp - 4], 2`
- `005FB4E9: mov byte ptr [ebp - 4], 3`
- `005FB4F7: mov byte ptr [ebp - 4], 2`
- `005FB633: mov dword ptr [ebp - 4], 1`
- `005FB7B9: mov dword ptr [ebp - 4], 2`
- `005FB7E5: mov byte ptr [ebp - 4], 3`
- `005FB7F3: mov byte ptr [ebp - 4], 2`
- `005FB8C3: mov byte ptr [ebp - 4], 1`
- `005FBA3D: and dword ptr [esi + 0x170], 0`
- `005FBA7A: and dword ptr [esi + 0x170], 0`
- `005FBAA6: mov byte ptr [ebp - 4], 1`
- `005FBAC8: mov byte ptr [ebp - 4], 2`
- `005FBAE7: mov byte ptr [ebp - 4], 3`
- `005FBAFB: mov byte ptr [ebp - 4], 3`
- `005FBB14: mov byte ptr [ebp - 4], 5`
- `005FBB41: mov byte ptr [ebp - 4], 3`
- `005FBB59: mov byte ptr [ebp - 4], 2`
- `005FBB6D: mov byte ptr [ebp - 4], 1`
- `005FBB85: mov byte ptr [ebp - 4], 6`
- `005FBC1C: mov byte ptr [ebp - 4], 6`
- `005FBC30: mov byte ptr [ebp - 4], 1`
- `005FBC73: mov byte ptr [ebp - 4], 1`
- `005FBCB5: mov byte ptr [ebp - 4], 1`
- `005FBD2E: mov byte ptr [ebp - 4], 1`
- `005FBD52: mov byte ptr [ebp - 4], 1`
- `005FBD7D: cmp dword ptr [ebp - 0x14], 2`
- `005FBE74: mov byte ptr [ebp - 4], 1`
- `005FBF61: mov byte ptr [ebp - 4], 1`
- `005FBFA4: mov byte ptr [ebp - 4], 1`
- `005FBFE6: mov byte ptr [ebp - 4], 1`
- `005FC058: mov byte ptr [ebp - 4], 1`
- `005FC079: mov byte ptr [ebp - 4], 1`
- `005FC0A4: cmp dword ptr [ebp - 0x14], 2`
- `005FC0E4: cmp dword ptr [ecx + 0x168], 4`
- `005FC10E: cmp dword ptr [esi + 0x168], 4`
- `005FC121: cmp dword ptr [0xbeda34], 0`
- `005FC1F1: cmp dword ptr [esi + 0x180], 1`
- `005FC280: cmp dword ptr [ecx + 0x16c], 0`
- `005FC289: cmp dword ptr [esp + 4], 0`
- `005FC2B3: cmp dword ptr [esp + 8], 0`
- `005FC3E9: mov dword ptr [esi], 1`
- `005FC3F4: and dword ptr [esi], 0`
- `005FC435: and dword ptr [ebp - 4], 0`
- `005FC481: and dword ptr [ebp - 4], 0`
- `005FC551: mov dword ptr [ebp - 4], 1`
- `005FC562: cmp dword ptr [ebp - 0x14], 1`
- `005FC5CE: mov dword ptr [ebp - 4], 2`
- `005FC5DF: cmp dword ptr [ebp - 0x14], 4`
- `005FC627: mov dword ptr [ebp - 4], 3`
- `005FC638: cmp dword ptr [ebp - 0x14], 4`
- `005FC6A3: and dword ptr [ebp - 4], 0`
- `005FC6FC: and dword ptr [ebp - 4], 0`
- `005FC794: and dword ptr [ebp - 4], 0`
- `005FC7AF: and dword ptr [ecx], 0`
- `005FC9F0: mov dword ptr [ebp - 4], 4`
- `005FCA21: mov byte ptr [ebp - 4], 5`
- `005FCA60: mov byte ptr [ebp - 4], 6`
- `005FCA8E: mov byte ptr [ebp - 4], 5`
- `005FCAA9: mov byte ptr [ebp - 4], 4`
- `005FCAE2: mov byte ptr [ebp - 4], 2`
- `005FCB20: mov byte ptr [ebp - 4], 3`
- `005FCB4E: mov byte ptr [ebp - 4], 2`
- `005FCB82: cmp dword ptr [eax + 0x24], 1`
- `005FCBFD: and dword ptr [ebp - 0x10], 0`
- `005FCC12: and dword ptr [ebp + 0xc], 0`
- `005FCC51: and dword ptr [esi], 0`
- `005FCC62: and byte ptr [ebp - 4], 0`
- `005FCE01: and byte ptr [ebp - 0x24], 0`
- `005FCE05: and dword ptr [ebp - 0x14], 0`
- `005FCE1E: and dword ptr [ebp - 4], 0`
- `005FCE38: cmp dword ptr [eax + 0x1a0], 6`
- `005FCE52: mov dword ptr [ebp - 0x10], 1`
- `005FCE76: cmp byte ptr [eax + 0x198], 0`
- `005FCE7F: cmp byte ptr [eax + 0x199], 0`
- `005FCE88: and dword ptr [ebp - 0x10], 0`
- `005FCE96: cmp dword ptr [ebp - 0x10], 0`
- `005FCEA6: and dword ptr [ebp - 0x10], 0`
- `005FCEB4: cmp dword ptr [ebp - 0x10], 0`
- `005FCEE3: and byte ptr [ebp - 0x231], 0`
- `005FCFBC: cmp dword ptr [edi + 0x214], 2`
- `005FD040: and dword ptr [ebp - 4], 0`
- `005FD08D: mov dword ptr [ebp - 4], 1`
- `005FD0A4: cmp dword ptr [ebp - 0x10], 0`
- `005FD0F3: cmp byte ptr [edi + 0x234], 0`
- `005FD14D: cmp byte ptr [esi + 0x234], 0`
- `005FD19B: and dword ptr [ebp - 0x14], 0`
- `005FD1A0: and dword ptr [ebp - 4], 0`
- `005FD1A4: cmp byte ptr [esi + 0x234], 0`
- `005FD1BC: cmp dword ptr [ebp + 0xc], 0`
- `005FD242: cmp dword ptr [ebp + 0xc], 0`
- `005FD3D2: mov dword ptr [esi + 0x134], 1`
- `005FD491: mov byte ptr [ebp - 4], 2`
- `005FD4B0: mov byte ptr [ebp - 4], 3`
- `005FD4CD: mov byte ptr [ebp - 4], 2`
- `005FD4EF: mov byte ptr [ebp - 4], 4`
- `005FD50C: mov byte ptr [ebp - 4], 2`
- `005FD52A: mov byte ptr [ebp - 4], 5`
- `005FD53E: mov byte ptr [ebp - 4], 6`
- `005FD557: mov byte ptr [ebp - 4], 6`
- `005FD591: mov byte ptr [ebp - 4], 6`
- `005FD5A9: mov byte ptr [ebp - 4], 5`
- `005FD5C1: mov byte ptr [ebp - 4], 2`
- `005FD5D8: mov byte ptr [ebp - 4], 1`
- `005FD605: mov byte ptr [ebp - 4], 1`
- `005FD674: and dword ptr [ebp - 4], 0`
- `005FD689: and byte ptr [ebp - 0x1014], 0`
- `005FD6DC: mov dword ptr [ebp - 4], 1`
- `005FD704: and byte ptr [eax], 0`
- `005FD74B: cmp dword ptr [eax + 0x201c], 0`
- `005FD8E8: and dword ptr [eax], 0`
- `005FD8F7: and dword ptr [0xbeda74], 0`
- `005FD9AA: and dword ptr [ebp - 4], 0`
- `005FD9CF: cmp dword ptr [esi + 4], 0`
- `005FD9DC: and dword ptr [esi + 4], 0`
- `005FD9E5: cmp dword ptr [esi + 4], 0`
- `005FD9F2: and dword ptr [esi + 4], 0`
- `005FD9FB: cmp dword ptr [esi + 4], 0`
- `005FDA08: and dword ptr [esi + 4], 0`
- `005FDA11: cmp dword ptr [esi + 4], 0`
- `005FDA1E: and dword ptr [esi + 4], 0`
- `005FDA44: cmp dword ptr [esi + 4], 0`
- `005FDA51: and dword ptr [esi + 4], 0`
- `005FDD26: and dword ptr [edi], 0`
- `005FDDA0: and dword ptr [esi], 0`
- `005FDE18: and dword ptr [edi], 0`
- `005FDF18: and dword ptr [esi + 0x10], 0`
- `005FDF1C: and dword ptr [esi + 0xc], 0`
- `005FDF20: and dword ptr [esi + 8], 0`
- `005FDF5C: and dword ptr [ebx], 0`
- `005FE01B: and dword ptr [esi], 0`
- `005FE155: and dword ptr [esi], 0`
- `005FF5CB: mov dword ptr [ebp - 4], 1`
- `005FF5D7: and byte ptr [ebp - 4], 0`
- `005FF63A: and dword ptr [ebx], 0`
- `005FFBB4: and dword ptr [ebp - 4], 0`
- `005FFBC3: and dword ptr [esi + 4], 0`
- `005FFBEE: and dword ptr [eax], 0`
- `005FFC3F: and dword ptr [eax + 8], 0`
- `005FFC4F: and dword ptr [eax + 4], 0`
- `005FFC5F: and dword ptr [eax + 4], 0`
- `005FFC70: or byte ptr [0xbf6ad0], 1`
- `005FFC77: and dword ptr [0xbf6b44], 0`
- `00601210: and dword ptr [esi], 0`
- `006012BD: and dword ptr [ebp - 4], 0`
- `006012C4: cmp dword ptr [edi], 0`
- `006012E1: and dword ptr [esi], 0`
- `00601372: and dword ptr [ebp - 4], 0`
- `0060138A: and dword ptr [eax], 0`
- `00601390: and dword ptr [esi + 0x74], 0`
- `006013A6: mov byte ptr [ebp - 4], 2`
- `006013CC: mov byte ptr [ebp - 4], 3`
- `00601451: mov dword ptr [ebp - 4], 2`
- `00601462: mov byte ptr [ebp - 4], 1`
- `0060146E: and dword ptr [0xbeda54], 0`
- `006014A9: mov dword ptr [ebp - 0x20], 1`
- `006014D2: mov byte ptr [ebp - 4], 1`
- `00601508: mov byte ptr [ebp - 4], 2`
- `00601553: mov byte ptr [ebp - 4], 3`
- `00601578: mov byte ptr [ebp - 4], 4`
- `006015CB: mov byte ptr [ebp - 4], 5`
- `006015F0: mov byte ptr [ebp - 4], 6`
- `00601706: cmp dword ptr [esi + 0x70], 3`
- `0060170F: and dword ptr [eax], 0`
- `0060171B: mov dword ptr [esi + 0x70], 2`
- `00601745: cmp dword ptr [esi + 0x70], 0`
- `0060174B: and dword ptr [esi + 0x70], 0`
- `006017AE: cmp dword ptr [esp + 4], 0`
- `00601864: cmp dword ptr [eax + 0x170], 0`
- `0060186D: cmp dword ptr [eax + 0x168], 2`
- `006018C1: mov byte ptr [ebp - 4], 2`
- `00601919: mov byte ptr [ebp - 4], 5`
- `00601934: mov byte ptr [ebp - 4], 4`
- `006019A2: mov byte ptr [ebp - 4], 6`
- `006019B9: mov byte ptr [ebp - 4], 4`
- `00601A35: mov byte ptr [ebp - 4], 4`
- `00601AC5: mov byte ptr [ebp - 4], 4`
- `00602447: cmp dword ptr [ebp - 0x14], 0`
- `006026B8: mov dword ptr [ebp - 0x54], 1`
- `006026F7: mov byte ptr [ebp - 4], 4`
- `00602706: and byte ptr [ebp - 4], 0`
- `00602794: mov byte ptr [ebp - 4], 2`
- `006027BA: mov byte ptr [ebp - 4], 3`
- `006027D1: mov byte ptr [ebp - 4], 4`
- `006027DE: mov byte ptr [ebp - 4], 5`
- `006027FF: mov byte ptr [ebp - 4], 5`
- `00602814: mov byte ptr [ebp - 4], 4`
- `00602824: mov byte ptr [ebp - 4], 3`
- `0060283C: mov byte ptr [ebp - 4], 2`
- `00602892: cmp dword ptr [ebx], 0`
- `006028FB: mov byte ptr [ebp - 4], 2`
- `00602980: mov byte ptr [ebp - 4], 2`
- `006029BA: mov byte ptr [ebp - 4], 3`
- `00602AB1: mov byte ptr [ebp - 4], 1`
- `00602ABD: and dword ptr [0xbeda50], 0`
- `00602B80: mov byte ptr [ebp - 4], 1`
- `00602BB4: mov byte ptr [ebp - 4], 2`
- `00602BD0: mov byte ptr [ebp - 4], 3`
- `00602BEC: mov byte ptr [ebp - 4], 3`
- `00602C05: mov byte ptr [ebp - 4], 5`
- `00602D29: and dword ptr [ebp - 0x5c], 0`
- `006031C3: cmp dword ptr [eax + 0xe4], 0`
- `00603278: and dword ptr [ebp - 0x20], 0`
- `00603D5A: mov byte ptr [ebp - 4], 1`
- `00603D66: and byte ptr [ebp - 4], 0`
- `00603E0C: mov byte ptr [ebp - 4], 1`
- `00603E15: and byte ptr [ebp - 4], 0`
- `00603E44: mov byte ptr [ebp - 4], 2`
- `00603E54: mov byte ptr [ebp - 4], 3`
- `00603E61: mov byte ptr [ebp - 4], 5`
- `00603E96: and byte ptr [ebp - 4], 0`
- `00603ECC: mov byte ptr [ebp - 4], 6`
- `00603F40: mov byte ptr [ebp - 4], 6`
- `00603F54: and byte ptr [ebp - 4], 0`
- `00603F75: mov dword ptr [ebx + 0xdc], 1`
- `00603F96: and byte ptr [ebp - 4], 0`
- `00604008: and dword ptr [ebp - 4], 0`
- `0060403A: mov byte ptr [ebp - 4], 1`
- `0060405A: mov byte ptr [ebp - 4], 2`
- `00604070: mov byte ptr [ebp - 4], 3`
- `00604086: mov byte ptr [ebp - 4], 4`
- `0060409C: mov byte ptr [ebp - 4], 5`
- `0060423E: mov byte ptr [ebp - 4], 6`
- `0060425B: mov byte ptr [ebp - 4], 5`
- `00604270: mov byte ptr [ebp - 4], 4`
- `00604285: mov byte ptr [ebp - 4], 3`
- `0060429A: mov byte ptr [ebp - 4], 2`
- `006042B3: mov byte ptr [ebp - 4], 1`
- `006042BC: and dword ptr [0xbeda4c], 0`
- `0060432C: mov byte ptr [ebp - 4], 1`
- `00604343: mov byte ptr [ebp - 4], 1`
- `0060435C: mov byte ptr [ebp - 4], 3`
- `006043AE: mov byte ptr [ebp - 4], 6`
- `006043C6: mov byte ptr [ebp - 4], 5`
- `0060440E: mov byte ptr [ebp - 4], 5`
- `006044FA: mov byte ptr [ebp - 4], 5`
- `00604506: cmp dword ptr [ebp - 0x48], 2`
- `00604545: mov byte ptr [ebp - 4], 5`
- `0060459D: mov byte ptr [ebp - 4], 5`
- `006045E0: mov byte ptr [ebp - 4], 5`
- `00604630: mov byte ptr [ebp - 4], 5`
- `00604706: mov byte ptr [ebp - 4], 5`
- `0060480C: mov byte ptr [ebp - 4], 5`
- `006048AF: mov byte ptr [ebp - 4], 5`
- `0060499B: mov byte ptr [ebp - 4], 5`
- `00604A3E: mov byte ptr [ebp - 4], 5`
- `00604B44: mov byte ptr [ebp - 4], 5`
- `00604BE7: mov byte ptr [ebp - 4], 5`
- `00604CD3: mov byte ptr [ebp - 4], 5`
- `00604D25: mov byte ptr [ebp - 4], 5`
- `00604DEE: mov byte ptr [ebp - 4], 5`
- `00604F2A: mov byte ptr [ebp - 4], 5`
- `00604FE7: cmp dword ptr [ecx], 0`
- `00605094: mov byte ptr [ebp - 4], 1`
- `006050BA: mov byte ptr [ebp - 4], 2`
- `00605105: mov byte ptr [ebp - 4], 1`
- `00605111: and byte ptr [ebp - 4], 0`
- `006051E5: cmp dword ptr [edi], 0`
- `0060535C: cmp dword ptr [eax + 0xf4], 0`
- `0060538D: cmp dword ptr [esi], 0`
- `00605390: mov dword ptr [ebp - 4], 1`
- `006053E3: cmp dword ptr [eax + 0xf8], 0`
- `00605414: cmp dword ptr [esi], 0`
- `00605417: mov dword ptr [ebp - 4], 2`
- `0060549A: mov dword ptr [ebp - 4], 3`
- `00605501: cmp dword ptr [eax + 0xf0], 0`
- `00605532: cmp dword ptr [esi], 0`
- `00605535: mov dword ptr [ebp - 4], 4`
- `00605588: cmp dword ptr [eax + 0xf4], 0`
- `006055B9: cmp dword ptr [esi], 0`
- `006055BC: mov dword ptr [ebp - 4], 5`
- `0060560C: cmp dword ptr [eax + 0xf8], 0`
- `0060563D: cmp dword ptr [esi], 0`
- `00605640: mov dword ptr [ebp - 4], 6`
- `0060570C: cmp dword ptr [eax + 0xf0], 0`
- `0060573D: cmp dword ptr [esi], 0`
- `00605793: cmp dword ptr [eax + 0xf4], 0`
- `006057C4: cmp dword ptr [esi], 0`
- `006058F3: cmp dword ptr [esp + 4], 0`
- `00605937: cmp dword ptr [edi + 0x104], 0`
- `00605946: cmp dword ptr [edi + 0x108], 0`
- `00605967: and dword ptr [esi], 0`
- `006059B3: cmp dword ptr [eax], 0`
- `00605A01: and dword ptr [ebp + 8], 0`
- `00605A3D: cmp dword ptr [ebp + 8], 3`
- `00605ACB: mov dword ptr [ebp - 4], 1`
- `00605B21: cmp dword ptr [ebp - 0x14], 3`
- `00605BA4: mov byte ptr [ebp - 4], 2`
- `00605BFD: mov byte ptr [ebp - 4], 3`
- `00605C1F: mov byte ptr [ebp - 4], 3`
- `00605C36: mov byte ptr [ebp - 4], 2`
- `00605CC9: mov byte ptr [ebp - 4], 5`
- `00605D12: mov byte ptr [ebp - 4], 2`
- `00605D4D: mov byte ptr [ebp - 4], 6`
- `00605DAA: mov byte ptr [ebp - 4], 2`
- `00605E2D: mov byte ptr [ebp - 4], 2`
- `00605ED3: mov byte ptr [ebp - 4], 2`
- `00605F5F: mov byte ptr [ebp - 4], 2`
- `00605F9E: mov byte ptr [ebp - 4], 5`
- `00605FB9: mov byte ptr [ebp - 4], 4`
- `00606020: mov byte ptr [ebp - 4], 6`
- `00606037: mov byte ptr [ebp - 4], 4`
- `006060B4: mov byte ptr [ebp - 4], 4`
- `00606144: mov byte ptr [ebp - 4], 4`
- `0060672E: cmp dword ptr [ebp - 0x14], 0`
- `00606797: cmp dword ptr [ebp - 0x14], 0`
- `00606909: cmp dword ptr [ebp - 0x14], 0`
- `00606989: cmp dword ptr [ebp - 0x14], 0`
- `00606AAD: cmp dword ptr [ebp - 0x14], 0`
- `00606B3A: mov dword ptr [ebp - 0x4c], 1`
- `00606B79: mov byte ptr [ebp - 4], 4`
- `00606B88: and byte ptr [ebp - 4], 0`
- `00606C3C: mov byte ptr [ebp - 4], 1`
- `00606C5F: mov byte ptr [ebp - 4], 2`
- `00606C71: mov byte ptr [ebp - 4], 3`
- `00606C84: mov byte ptr [ebp - 4], 5`
- `00606D13: mov dword ptr [ebp - 4], 6`
- `00606D71: mov byte ptr [ebp - 4], 6`
- `006070EE: cmp dword ptr [ebx + eax*4 + 0xc4], 0`
- `00607145: cmp dword ptr [esi], 0`
- `006071F7: cmp dword ptr [ebx + eax*4 + 0xc4], 0`
- `006074AB: mov byte ptr [ebp - 4], 2`
- `006074E3: mov byte ptr [ebp - 4], 3`
- `006075B2: mov byte ptr [ebp - 4], 1`
- `006075BE: and dword ptr [0xbeda3c], 0`
- `0060766C: mov byte ptr [ebp - 4], 1`
- `00607679: mov byte ptr [ebp - 4], 2`
- `0060768D: mov byte ptr [ebp - 4], 3`
- `006076B1: mov byte ptr [ebp - 4], 4`
- `006076CF: mov byte ptr [ebp - 4], 4`
- `006076E4: mov byte ptr [ebp - 4], 3`
- `006076F8: mov byte ptr [ebp - 4], 2`
- `00607710: mov byte ptr [ebp - 4], 1`
- `0060773C: and dword ptr [ebp - 0x7c], 0`
- `00607752: mov byte ptr [ebp - 4], 6`
- `006077C3: mov byte ptr [ebp - 4], 6`
- `0060786D: mov byte ptr [ebp - 4], 6`
- `0060791D: mov byte ptr [ebp - 4], 6`
- `006079CA: mov byte ptr [ebp - 4], 6`
- `00607A77: mov byte ptr [ebp - 4], 6`
- `00607B24: mov byte ptr [ebp - 4], 6`
- `00607BCE: mov byte ptr [ebp - 4], 6`
- `00608965: mov byte ptr [ebp - 4], 6`
- `00608971: mov byte ptr [ebp - 4], 1`
- `0060897D: and byte ptr [ebp - 4], 0`
- `00608A34: mov byte ptr [ebp - 4], 4`
- `00608A52: mov byte ptr [ebp - 4], 5`
- `00608A72: mov byte ptr [ebp - 4], 6`
- `00608A7B: and dword ptr [esi + 0x3a6c], 0`
- `00608C0A: mov byte ptr [ebp - 4], 6`
- `00608C23: mov byte ptr [ebp - 4], 5`
- `00608C3F: mov byte ptr [ebp - 4], 4`
- `00608C4B: mov byte ptr [ebp - 4], 3`
- `00608C57: mov byte ptr [ebp - 4], 2`
- `00608C63: mov byte ptr [ebp - 4], 1`
- `00608C6C: and dword ptr [0xbeda38], 0`
- `00608CEE: mov byte ptr [ebp - 4], 1`
- `00608CFE: mov byte ptr [ebp - 4], 2`
- `00608D29: mov dword ptr [ebp - 0x4c], 1`
- `00608D3F: mov dword ptr [ebp - 4], 3`
- `00608D56: mov byte ptr [ebp - 4], 4`
- `00608D62: mov byte ptr [ebp - 4], 3`
- `00608D81: mov byte ptr [ebp - 4], 5`
- `00608D96: mov byte ptr [ebp - 4], 3`
- `00608DCA: mov byte ptr [ebp - 4], 6`
- `00608DE2: mov byte ptr [ebp - 4], 3`
- `0060904D: cmp dword ptr [ebp - 0x18], 2`
- `006093D0: mov byte ptr [ebp - 4], 3`
- `006095D8: and dword ptr [ebp - 4], 0`
- `006095EE: mov byte ptr [ebp - 4], 1`
- `006095FB: mov byte ptr [ebp - 4], 2`
- `00609636: mov dword ptr [ebp - 4], 3`
- `00609652: mov byte ptr [ebp - 4], 3`
- `006096A2: mov dword ptr [ebp - 4], 5`
- `006096B6: mov byte ptr [ebp - 4], 6`
- `0060970D: mov byte ptr [ebp - 4], 5`
- `00609739: cmp dword ptr [esi], 0`
- `00609789: cmp dword ptr [esi], 0`
- `006097F4: cmp dword ptr [edi], 0`
- `00609844: cmp dword ptr [edi], 0`
- `006098E1: cmp dword ptr [esi], 0`
- `006099BC: mov byte ptr [ebp - 4], 1`
- `00609A04: and byte ptr [ebp - 4], 0`
- `00609A73: mov dword ptr [ebp - 4], 2`
- `00609A81: mov byte ptr [ebp - 4], 3`
- `00609AC1: mov byte ptr [ebp - 4], 2`
- `00609AE1: cmp dword ptr [ebx], 0`
- `00609B21: mov dword ptr [ebp - 4], 4`
- `00609B2D: cmp dword ptr [ebx], 0`
- `00609B30: mov byte ptr [ebp - 4], 5`
- `00609B6D: mov byte ptr [ebp - 4], 4`
- `00609B9F: mov dword ptr [ebp - 4], 6`
- `00609BAB: cmp dword ptr [ebx], 0`
- `00609BDA: mov byte ptr [ebp - 4], 6`
- `00609C58: and dword ptr [ebp - 4], 0`
- `00609C6D: mov byte ptr [ebp - 4], 1`
- `00609CC4: and byte ptr [ebp - 4], 0`
- `00609D32: mov dword ptr [ebp - 4], 2`
- `00609D3E: cmp dword ptr [ebx], 0`
- `00609D41: mov byte ptr [ebp - 4], 3`
- `00609D81: mov byte ptr [ebp - 4], 2`
- `00609DA1: cmp dword ptr [ebx], 0`
- `00609DE1: mov dword ptr [ebp - 4], 4`
- `00609DED: cmp dword ptr [ebx], 0`
- `00609DF0: mov byte ptr [ebp - 4], 5`
- `00609E2D: mov byte ptr [ebp - 4], 4`
- `00609E5F: mov dword ptr [ebp - 4], 6`
- `00609E6B: cmp dword ptr [ebx], 0`
- `00609EB2: mov byte ptr [ebp - 4], 6`
- `00609F72: mov dword ptr [ebp - 4], 1`
- `0060A0D8: and dword ptr [ebp - 4], 0`
- `0060A0EE: mov byte ptr [ebp - 4], 1`
- `0060A0FB: mov byte ptr [ebp - 4], 2`
- `0060A135: mov dword ptr [ebp - 4], 3`
- `0060A152: mov byte ptr [ebp - 4], 3`
- `0060A1A2: mov dword ptr [ebp - 4], 5`
- `0060A1B6: mov byte ptr [ebp - 4], 6`
- `0060A20D: mov byte ptr [ebp - 4], 5`
- `0060A239: cmp dword ptr [esi], 0`
- `0060A289: cmp dword ptr [esi], 0`
- `0060A2F4: cmp dword ptr [edi], 0`
- `0060A344: cmp dword ptr [edi], 0`
- `0060A3E1: cmp dword ptr [esi], 0`
- `0060A518: and dword ptr [ebp - 4], 0`
- `0060A51C: cmp dword ptr [edi + esi*4 + 0x397c], 0`
- `0060A54D: mov byte ptr [ebp - 4], 2`
- `0060A561: cmp dword ptr [ebx], 0`
- `0060A577: cmp dword ptr [ebx], 0`
- `0060A5B9: mov byte ptr [ebp - 4], 3`
- `0060A5CB: mov byte ptr [ebp - 4], 3`
- `0060A5E2: mov byte ptr [ebp - 4], 2`
- `0060A638: and dword ptr [ebp + 8], 0`
- `0060A672: mov byte ptr [ebp - 4], 5`
- `0060A6BB: mov byte ptr [ebp - 4], 2`
- `0060A6F3: mov byte ptr [ebp - 4], 6`
- `0060A753: mov byte ptr [ebp - 4], 2`
- `0060A7D6: mov byte ptr [ebp - 4], 2`
- `0060A86B: mov byte ptr [ebp - 4], 2`
- `0060A9BA: mov byte ptr [ebp - 4], 2`
- `0060AA32: mov byte ptr [ebp - 4], 3`
- `0060AA44: mov byte ptr [ebp - 4], 3`
- `0060AA5B: mov byte ptr [ebp - 4], 2`
- `0060AA6F: cmp dword ptr [ebp + 8], 0`
- `0060AAA9: and dword ptr [ebp - 0x10], 0`
- `0060AAD3: mov byte ptr [ebp - 4], 5`
- `0060AB1C: mov byte ptr [ebp - 4], 2`
- `0060AB5E: mov byte ptr [ebp - 4], 6`
- `0060ABA6: mov byte ptr [ebp - 4], 2`
- `0060AC22: mov byte ptr [ebp - 4], 2`
- `0060ACB5: mov byte ptr [ebp - 4], 2`
- `0060AD41: and dword ptr [ebp - 4], 0`
- `0060AD45: cmp dword ptr [esi + edi*4 + 0x3a70], 0`
- `0060AD78: mov byte ptr [ebp - 4], 2`
- `0060ADB7: mov byte ptr [ebp - 4], 3`
- `0060ADFF: mov byte ptr [ebp - 4], 2`
- `0060AE27: mov byte ptr [ebp - 4], 4`
- `0060AE5A: mov byte ptr [ebp - 4], 5`
- `0060AE8A: mov byte ptr [ebp - 4], 6`
- `0060AEAB: mov byte ptr [ebp - 4], 5`
- `0060AEC3: mov byte ptr [ebp - 4], 4`
- `0060AEDC: mov byte ptr [ebp - 4], 2`
- `0060AFB0: cmp dword ptr [esp + 4], 0`
- `0060AFD8: cmp dword ptr [eax + 0x170], 0`
- `0060AFE1: cmp dword ptr [eax + 0x168], 5`
- `0060B005: and dword ptr [0xbeda84], 0`
- `0060B036: and dword ptr [eax + 4], 0`
- `0060B03B: and dword ptr [0xbeda54], 0`
- `0060B043: and dword ptr [0xbeda50], 0`
- `0060B04B: and dword ptr [0xbeda4c], 0`
- `0060B053: and dword ptr [0xbeda3c], 0`
- `0060B05B: and dword ptr [0xbeda38], 0`
- `0060C38C: or byte ptr [0xbf6ad0], 1`
- `0060C393: and dword ptr [0xbf6b44], 0`
- `0060D850: mov byte ptr [ebp - 4], 3`
- `0060D8A3: mov byte ptr [ebp - 4], 4`
- `0060D8C4: mov byte ptr [ebp - 4], 5`
- `0060D8CF: mov byte ptr [ebp - 4], 4`
- `0060D8F2: mov byte ptr [ebp - 4], 6`
- `0060D903: mov byte ptr [ebp - 4], 4`
- `0060D934: mov byte ptr [ebp - 4], 3`
- `0060D9A6: mov dword ptr [ebp - 4], 2`
- `0060D9BD: mov byte ptr [ebp - 4], 1`
- `0060D9CF: and byte ptr [ebp - 4], 0`
- `0060DA1F: and dword ptr [ebp - 4], 0`
- `0060DA5E: mov dword ptr [ebp - 4], 1`
- `0060DABA: mov dword ptr [ebp - 4], 2`
- `0060DACF: mov byte ptr [ebp - 4], 2`
- `0060DB27: mov dword ptr [ebp - 4], 4`
- `0060DB3D: mov byte ptr [ebp - 4], 4`
- `0060DBC7: mov byte ptr [ebp - 4], 2`
- `0060DC06: mov byte ptr [ebp - 4], 3`
- `0060DC23: mov byte ptr [ebp - 4], 3`
- `0060DC3A: mov byte ptr [ebp - 4], 2`
- `0060DC5B: mov byte ptr [ebp - 4], 5`
- `0060DC6E: mov byte ptr [ebp - 4], 6`
- `0060DCC2: mov byte ptr [ebp - 4], 6`
- `0060DCD2: mov byte ptr [ebp - 4], 5`
- `0060DCEA: mov byte ptr [ebp - 4], 2`
- `0060DD55: mov byte ptr [ebp - 4], 2`
- `0060DE2C: mov byte ptr [ebp - 4], 2`
- `0060DE43: mov byte ptr [ebp - 4], 1`
- `0060DE4C: and byte ptr [ebp - 4], 0`
- `0060DED6: mov byte ptr [ebp - 4], 1`
- `0060DEEF: mov byte ptr [ebp - 4], 2`
- `0060DF02: mov byte ptr [ebp - 4], 5`
- `0060DF2E: mov byte ptr [ebp - 4], 4`
- `0060DF6D: mov dword ptr [ebp - 4], 6`
- `0060DFFF: mov byte ptr [ebp - 4], 6`
- `0060E093: mov byte ptr [ebp - 4], 6`
- `0060E10E: mov byte ptr [ebp - 4], 6`
- `0060E170: and dword ptr [ebp - 4], 0`
- `0060E1A6: mov byte ptr [ebp - 4], 1`
- `0060E1AF: and dword ptr [esi + 0xfc], 0`
- `0060E1CC: mov byte ptr [ebp - 4], 2`
- `0060E1D0: mov dword ptr [esi + 0xf8], 4`
- `0060E25D: mov dword ptr [ebp - 4], 1`
- `0060E269: and byte ptr [ebp - 4], 0`
- `0060E2F9: mov dword ptr [ebp - 4], 1`
- `0060E32C: mov dword ptr [ebp - 4], 2`
- `0060E35F: mov dword ptr [ebp - 4], 3`
- `0060E392: mov dword ptr [ebp - 4], 4`
- `0060E3C4: mov dword ptr [ebp - 4], 5`
- `0060E3D6: mov byte ptr [ebp - 4], 6`
- `0060E45C: mov byte ptr [ebp - 4], 5`
- `0060E5D4: and dword ptr [ebp - 4], 0`
- `0060E5D8: cmp dword ptr [esi], 0`
- `0060E6E8: mov dword ptr [ebp - 4], 1`
- `0060E75D: mov dword ptr [ebp - 4], 2`
- `0060E7EB: mov dword ptr [ebp - 4], 3`
- `0060E814: mov byte ptr [ebp - 4], 4`
- `0060E821: mov byte ptr [ebp - 4], 5`
- `0060E840: mov byte ptr [ebp - 4], 6`
- `0060E89C: mov byte ptr [ebp - 4], 5`
- `0060E8AD: mov byte ptr [ebp - 4], 4`
- `0060E8BD: mov byte ptr [ebp - 4], 3`
- `0060E91D: cmp dword ptr [eax + 0x168], 1`
- `0060E9DB: mov dword ptr [ebp - 4], 1`
- `0060EADB: cmp dword ptr [ecx + 0x168], 1`
- `0060EAE9: cmp dword ptr [eax], 0`
- `0060EAF3: mov dword ptr [eax], 1`
- `0060EB79: and dword ptr [ebp - 4], 0`
- `0060EBBC: cmp dword ptr [esi + 4], 0`
- `0060EC08: mov byte ptr [ebp - 4], 2`
- `0060ECF9: mov dword ptr [ebp - 4], 5`
- `0060ED0D: mov byte ptr [ebp - 4], 4`
- `0060ED1F: mov byte ptr [ebp - 4], 3`
- `0060ED2E: mov byte ptr [ebp - 4], 2`
- `0060ED3D: mov byte ptr [ebp - 4], 1`
- `0060ED4C: and byte ptr [ebp - 4], 0`
- `0060ED93: and dword ptr [ebp - 4], 0`
- `0060EDD0: mov dword ptr [ebp - 4], 1`
- `0060EE07: mov byte ptr [ebp - 4], 2`
- `0060EE13: mov byte ptr [ebp - 4], 1`
- `0060EE68: and dword ptr [ebp - 4], 0`
- `0060EEA5: mov dword ptr [ebp - 4], 1`
- `0060EEDC: mov byte ptr [ebp - 4], 2`
- `0060EEE8: mov byte ptr [ebp - 4], 1`
- `0060EF79: mov dword ptr [ebp - 4], 1`
- `0060EFCD: mov byte ptr [ebp - 4], 2`
- `0060EFD9: mov byte ptr [ebp - 4], 1`
- `0060F045: and dword ptr [ebp - 4], 0`
- `0060F07F: mov dword ptr [ebp - 4], 1`
- `0060F088: cmp dword ptr [esi + 4], 0`
- `0060F0D0: mov byte ptr [ebp - 4], 2`
- `0060F0DC: mov byte ptr [ebp - 4], 1`
- `0060F13A: and dword ptr [ebp - 4], 0`
- `0060F174: mov dword ptr [ebp - 4], 1`
- `0060F17D: cmp dword ptr [esi + 4], 0`
- `0060F1C5: mov byte ptr [ebp - 4], 2`
- `0060F1D1: mov byte ptr [ebp - 4], 1`
- `0060F2C2: mov byte ptr [ebp - 4], 2`
- `0060F36E: mov byte ptr [ebp - 4], 1`
- `0060F3A9: mov byte ptr [ebp - 4], 2`
- `0060F3B9: mov byte ptr [ebp - 4], 2`
- `0060F3E5: mov byte ptr [ebp - 4], 4`
- `0060F403: mov byte ptr [ebp - 4], 2`
- `0060F45E: mov dword ptr [eax], 1`
- `0060F488: mov byte ptr [ebp - 4], 1`
- `0060F4AC: mov byte ptr [ebp - 4], 3`
- `0060F4CE: mov byte ptr [ebp - 4], 4`
- `0060F4FA: mov byte ptr [ebp - 4], 3`
- `0060F520: mov byte ptr [ebp - 4], 5`
- `0060F534: mov byte ptr [ebp - 4], 6`
- `0060F565: cmp dword ptr [ebp + 8], 0`
- `0060F5EA: mov byte ptr [ebp - 4], 6`
- `0060F602: mov byte ptr [ebp - 4], 5`
- `0060F61A: mov byte ptr [ebp - 4], 3`
- `0060F6B0: mov byte ptr [ebp - 4], 3`
- `0060F6D3: mov byte ptr [ebp - 4], 3`
- `0060F728: and dword ptr [ebp - 4], 0`
- `0060F78D: cmp dword ptr [ecx + 0x14], 0`
- `0060F8A3: mov byte ptr [ebp - 4], 1`
- `0060F8AC: and byte ptr [ebp - 4], 0`
- `0060F8CD: mov byte ptr [ebp - 4], 2`
- `0060F8E3: mov byte ptr [ebp - 4], 3`
- `0060F8FC: mov byte ptr [ebp - 4], 3`
- `0060F915: mov byte ptr [ebp - 4], 5`
- `0060F945: mov byte ptr [ebp - 4], 3`
- `0060F95D: mov byte ptr [ebp - 4], 2`
- `0060F971: and byte ptr [ebp - 4], 0`
- `0060F9B2: mov dword ptr [ebp - 0x20], 1`
- `0060F9C8: mov dword ptr [ebp - 4], 6`
- `0060F9EB: mov byte ptr [ebp - 4], 6`
- `0060FA22: mov byte ptr [ebp - 4], 6`
- `0060FA6E: mov byte ptr [ebp - 4], 6`
- `0060FAA0: mov byte ptr [ebp - 4], 6`
- `0060FAD7: mov dword ptr [ebp - 0x20], 1`
- `0060FBFA: mov dword ptr [ebp - 0x20], 1`
- `0060FD1D: mov dword ptr [ebp - 0x20], 1`
- `0060FE40: mov dword ptr [ebp - 0x20], 1`
- `0060FEE6: mov dword ptr [ebp - 0x20], 1`
- `0060FF9E: mov dword ptr [ebp - 0x20], 1`
- `006100BD: and dword ptr [ebp - 0x88], 0`
- `006100E0: mov dword ptr [ebp - 0x84], 1`
- `00610168: mov dword ptr [ebp - 0x38], 1`
- `0061027A: and dword ptr [ebp - 4], 0`
- `006102E2: cmp dword ptr [esi + 0xd8], 6`
- `00610305: mov dword ptr [ebp - 4], 1`
- `006103A0: and dword ptr [ebp - 4], 0`
- `00610428: and dword ptr [ebp - 4], 0`
- `0061043C: cmp dword ptr [esi], 0`
- `0061043F: mov byte ptr [ebp - 4], 1`
- `00610480: and byte ptr [ebp - 4], 0`
- `006104C6: cmp dword ptr [esp + 0xc], 0`
- `00610547: mov byte ptr [ebp - 4], 1`
- `00610557: mov byte ptr [ebp - 4], 3`
- `006105C2: mov dword ptr [ebp - 4], 4`
- `006105F1: mov byte ptr [ebp - 4], 5`
- `0061063F: mov byte ptr [ebp - 4], 4`
- `00610674: mov dword ptr [ebx + 0x100], 1`
- `0061068C: mov dword ptr [ebp - 4], 6`
- `00610720: and dword ptr [0xbeda8c], 0`
- `0061077D: cmp dword ptr [esi + 4], 0`
- `0061078A: and dword ptr [esi + 4], 0`
- `006107B0: cmp dword ptr [esi + 4], 0`
- `006107BD: and dword ptr [esi + 4], 0`
- `00611BD0: or byte ptr [0xbf6ad0], 1`
- `00611BD7: and dword ptr [0xbf6b44], 0`
- `00613075: mov byte ptr [ebp - 4], 5`
- `00613177: mov byte ptr [ebp - 4], 6`
- `0061318F: and dword ptr [esi + 0x134], 0`
- `0061319C: mov byte ptr [ebp - 4], 4`
- `006131AB: mov byte ptr [ebp - 4], 3`
- `006131BC: mov byte ptr [ebp - 4], 2`
- `006131D0: mov byte ptr [ebp - 4], 1`
- `006131DC: and dword ptr [0xbeda70], 0`
- `00613242: mov byte ptr [ebp - 4], 1`
- `00613256: mov byte ptr [ebp - 4], 1`
- `0061326F: mov byte ptr [ebp - 4], 3`
- `0061329F: mov byte ptr [ebp - 4], 1`
- `006132B3: and byte ptr [ebp - 4], 0`
- `006132EE: mov dword ptr [ebp - 4], 4`
- `00613314: mov byte ptr [ebp - 4], 5`
- `00613325: mov byte ptr [ebp - 4], 6`
- `0061333D: mov byte ptr [ebp - 4], 5`
- `00613395: mov byte ptr [ebp - 4], 5`
- `006133CA: mov byte ptr [ebp - 4], 5`
- `006133FB: mov byte ptr [ebp - 4], 5`
- `0061342E: mov byte ptr [ebp - 4], 5`
- `0061347C: mov byte ptr [ebp - 4], 5`
- `006134AA: mov byte ptr [ebp - 4], 5`
- `006134D6: mov byte ptr [ebp - 4], 4`
- `00613502: cmp dword ptr [esi + 0x160], 0`
- `00613577: and dword ptr [ebp - 4], 0`
- `006135AA: mov byte ptr [ebp - 4], 1`
- `006135EC: and byte ptr [ebp - 4], 0`
- `00613693: cmp byte ptr [edi + 0x15c], 0`
- `006136B7: mov dword ptr [ebp - 0x10], 1`
- `006136BE: mov byte ptr [ebp - 4], 1`
- `006136EB: mov dword ptr [ebp - 4], 1`
- `00613737: mov byte ptr [ebp - 4], 3`
- `00613744: mov byte ptr [ebp - 4], 4`
- `00613762: mov byte ptr [ebp - 4], 5`
- `0061376F: mov byte ptr [ebp - 4], 5`
- `0061391C: mov byte ptr [ebp - 4], 3`
- `0061392B: and byte ptr [ebp - 4], 0`
- `006139EC: mov byte ptr [ebp - 4], 1`
- `006139FC: mov byte ptr [ebp - 4], 2`
- `00613A09: mov byte ptr [ebp - 4], 4`
- `00613A75: mov byte ptr [ebp - 4], 5`
- `00613A97: mov byte ptr [ebp - 4], 6`
- `00613AE4: mov byte ptr [ebp - 4], 5`
- `00613B19: mov dword ptr [eax + 0xd4], 1`
- `00613BAD: and dword ptr [0xbeda70], 0`
- `0061574B: mov byte ptr [ebp - 4], 6`
- `0061575F: mov byte ptr [ebp - 4], 5`
- `0061576E: mov byte ptr [ebp - 4], 4`
- `0061577C: mov byte ptr [ebp - 4], 3`
- `0061578D: mov byte ptr [ebp - 4], 2`
- `0061579E: mov byte ptr [ebp - 4], 1`
- `006157AA: and dword ptr [0xbeda6c], 0`
- `00615808: mov byte ptr [ebp - 4], 1`
- `00615814: and byte ptr [ebp - 4], 0`
- `0061583A: mov byte ptr [ebp - 4], 2`
- `0061584B: and byte ptr [ebp - 4], 0`
- `00615890: mov byte ptr [ebp - 4], 3`
- `006158A4: mov byte ptr [ebp - 4], 4`
- `006158B2: mov byte ptr [ebp - 4], 3`
- `006158D8: mov byte ptr [ebp - 4], 5`
- `00615904: mov byte ptr [ebp - 4], 3`
- `00615943: mov byte ptr [ebp - 4], 6`
- `00615951: mov byte ptr [ebp - 4], 3`
- `006159A3: mov byte ptr [ebp - 4], 3`
- `006159ED: mov byte ptr [ebp - 4], 3`
- `00615A3F: mov byte ptr [ebp - 4], 3`
- `00615B25: mov byte ptr [ebp - 4], 3`
- `00615BE5: mov byte ptr [ebp - 4], 3`
- `00615CA7: mov byte ptr [ebp - 4], 3`
- `00615CB0: cmp dword ptr [ebx + 0x74], 0`
- `00615CCF: cmp dword ptr [eax], 0`
- `00615D09: mov byte ptr [ebp - 4], 3`
- `00615D12: cmp dword ptr [esi], 0`
- `00615D30: cmp dword ptr [esi], 0`
- `00615D62: mov byte ptr [ebp - 4], 3`
- `00615E32: mov byte ptr [ebp - 4], 3`
- `00615EA3: mov byte ptr [ebp - 4], 3`
- `00615F7C: mov byte ptr [ebp - 4], 3`
- `0061604B: mov byte ptr [ebp - 4], 3`
- `00616060: mov dword ptr [eax + 0x214], 1`
- `00616153: mov byte ptr [ebp - 4], 3`
- `006161FE: mov byte ptr [ebp - 4], 3`
- `0061620A: and byte ptr [ebp - 4], 0`
- `00616836: mov byte ptr [ebp - 4], 1`
- `0061684D: mov byte ptr [ebp - 4], 2`
- `0061685F: mov byte ptr [ebp - 4], 3`
- `00616872: mov byte ptr [ebp - 4], 5`
- `006168A4: mov byte ptr [ebp - 4], 1`
- `006168E3: mov dword ptr [ebp - 4], 6`
- `00616948: mov byte ptr [ebp - 4], 6`
- `0061744D: mov dword ptr [ebp - 0x1c], 1`
- `0061759E: cmp dword ptr [ecx + 0x16c], 0`
- `006175B1: cmp dword ptr [ecx + 0x16c], 0`
- `006175C5: cmp dword ptr [esp + 4], 0`
- `00617629: and dword ptr [ebp - 4], 0`
- `00617699: cmp byte ptr [eax], 0`
- `006176C4: and dword ptr [ebp - 4], 0`
- `006176E9: cmp dword ptr [esp + 4], 0`
- `00617711: cmp dword ptr [eax + 0x170], 0`
- `0061771A: cmp dword ptr [eax + 0x168], 4`
- `0061777A: mov byte ptr [ebp - 4], 1`
- `00617807: mov dword ptr [ebp - 4], 2`
- `00617816: mov byte ptr [ebp - 4], 1`
- `0061781F: and byte ptr [ebp - 4], 0`
- `006178A2: and dword ptr [0xbeda48], 0`
- `006178E6: mov dword ptr [ebp - 0x24], 1`
- `0061790F: mov byte ptr [ebp - 4], 1`
- `0061793B: mov byte ptr [ebp - 4], 2`
- `00617989: mov byte ptr [ebp - 4], 3`
- `006179B0: mov byte ptr [ebp - 4], 4`
- `006179F8: mov byte ptr [ebp - 4], 5`
- `00617A0F: mov byte ptr [ebp - 4], 6`
- `00617A25: mov byte ptr [ebp - 4], 5`
- `00617A6C: mov byte ptr [ebp - 4], 5`
- `00617AFA: mov byte ptr [ebp - 4], 1`
- `00617B60: and dword ptr [0xbeda44], 0`
- `00617BA4: mov dword ptr [ebp - 0x24], 1`
- `00617BCD: mov byte ptr [ebp - 4], 1`
- `00617BF9: mov byte ptr [ebp - 4], 2`
- `00617C47: mov byte ptr [ebp - 4], 3`
- `00617C6E: mov byte ptr [ebp - 4], 4`
- `00617CB6: mov byte ptr [ebp - 4], 5`
- `00617CCD: mov byte ptr [ebp - 4], 6`
- `00617CE3: mov byte ptr [ebp - 4], 5`
- `00617D2A: mov byte ptr [ebp - 4], 5`
- `00617DB8: mov byte ptr [ebp - 4], 1`
- `00617E1E: and dword ptr [0xbeda40], 0`
- `00617E62: mov dword ptr [ebp - 0x24], 1`
- `00617E8B: mov byte ptr [ebp - 4], 1`
- `00617EB7: mov byte ptr [ebp - 4], 2`
- `00617F05: mov byte ptr [ebp - 4], 3`
- `00617F2C: mov byte ptr [ebp - 4], 4`
- `00617F74: mov byte ptr [ebp - 4], 5`
- `00617F8B: mov byte ptr [ebp - 4], 6`
- `00617FA1: mov byte ptr [ebp - 4], 5`
- `00617FE8: mov byte ptr [ebp - 4], 5`
- `0061805C: mov byte ptr [ebp - 4], 1`
- `00618088: mov byte ptr [ebp - 4], 2`
- `006180D5: mov byte ptr [ebp - 4], 1`
- `006180FF: mov byte ptr [ebp - 4], 3`
- `0061810D: mov byte ptr [ebp - 4], 1`
- `0061812D: mov byte ptr [ebp - 4], 4`
- `00618148: mov byte ptr [ebp - 4], 5`
- `0061816C: mov byte ptr [ebp - 4], 4`
- `0061817C: mov byte ptr [ebp - 4], 1`
- `00618231: mov byte ptr [ebp - 4], 1`
- `0061825D: and byte ptr [ebp - 4], 0`
- `00618342: cmp byte ptr [ecx], 0`
- `00618347: mov byte ptr [ecx], 1`
- `0061834C: and byte ptr [ecx], 0`
- `006183B8: cmp dword ptr [eax + 0x170], 0`
- `006183C1: cmp dword ptr [eax + 0x168], 4`
- `0061844A: and dword ptr [ebp - 4], 0`
- `0061847B: mov byte ptr [ebp - 4], 1`
- `00618491: mov byte ptr [ebp - 4], 2`
- `006184C3: mov byte ptr [ebp - 4], 6`
- `00618529: mov dword ptr [ebp - 4], 6`
- `0061853D: mov byte ptr [ebp - 4], 5`
- `0061854F: mov byte ptr [ebp - 4], 4`
- `0061855E: mov byte ptr [ebp - 4], 3`
- `00618578: mov byte ptr [ebp - 4], 2`
- `0061858A: mov byte ptr [ebp - 4], 1`
- `00618593: and dword ptr [0xbeda34], 0`
- `00618661: mov byte ptr [ebp - 4], 1`
- `00618678: mov byte ptr [ebp - 4], 1`
- `00618691: mov byte ptr [ebp - 4], 3`
- `006186E0: mov byte ptr [ebp - 4], 6`
- `006186F8: mov byte ptr [ebp - 4], 5`
- `00618790: mov byte ptr [ebp - 4], 5`
- `00618812: mov byte ptr [ebp - 4], 5`
- `00618895: mov byte ptr [ebp - 4], 5`
- `0061892E: mov byte ptr [ebp - 4], 5`
- `00618A22: mov byte ptr [ebp - 4], 5`
- `00618C43: mov dword ptr [ebp - 0x4c], 1`
- `00618E80: mov byte ptr [ebp - 4], 5`
- `00618EEA: mov byte ptr [ebp - 4], 1`
- `00618F16: mov byte ptr [ebp - 4], 2`
- `00618F63: mov byte ptr [ebp - 4], 1`
- `00618F8D: mov byte ptr [ebp - 4], 3`
- `00618F9B: mov byte ptr [ebp - 4], 1`
- `00618FBB: mov byte ptr [ebp - 4], 4`
- `00618FD6: mov byte ptr [ebp - 4], 5`
- `00618FFA: mov byte ptr [ebp - 4], 4`
- `0061900A: mov byte ptr [ebp - 4], 1`
- `006190BF: mov byte ptr [ebp - 4], 1`
- `006190EB: and byte ptr [ebp - 4], 0`
- `00619213: mov byte ptr [ebp - 4], 1`
- `0061922A: mov byte ptr [ebp - 4], 1`
- `00619243: mov byte ptr [ebp - 4], 3`
- `00619292: mov byte ptr [ebp - 4], 6`
- `006192AA: mov byte ptr [ebp - 4], 5`
- `00619342: mov byte ptr [ebp - 4], 5`
- `006193C4: mov byte ptr [ebp - 4], 5`
- `00619447: mov byte ptr [ebp - 4], 5`
- `006194E0: mov byte ptr [ebp - 4], 5`
- `006195D4: mov byte ptr [ebp - 4], 5`
- `006197F5: mov dword ptr [ebp - 0x4c], 1`
- `00619A32: mov byte ptr [ebp - 4], 5`
- `00619B4E: mov byte ptr [ebp - 4], 1`
- `00619B65: mov byte ptr [ebp - 4], 1`
- `00619B7E: mov byte ptr [ebp - 4], 3`
- `00619BCD: mov byte ptr [ebp - 4], 6`
- `00619BE5: mov byte ptr [ebp - 4], 5`
- `00619C7D: mov byte ptr [ebp - 4], 5`
- `00619CFF: mov byte ptr [ebp - 4], 5`
- `00619D82: mov byte ptr [ebp - 4], 5`
- `00619E1B: mov byte ptr [ebp - 4], 5`
- `00619F0F: mov byte ptr [ebp - 4], 5`
- `0061A130: mov dword ptr [ebp - 0x4c], 1`
- `0061A370: mov byte ptr [ebp - 4], 5`
- `0061A3DA: mov byte ptr [ebp - 4], 1`
- `0061A406: mov byte ptr [ebp - 4], 2`
- `0061A453: mov byte ptr [ebp - 4], 1`
- `0061A47D: mov byte ptr [ebp - 4], 3`
- `0061A48B: mov byte ptr [ebp - 4], 1`
- `0061A4AB: mov byte ptr [ebp - 4], 4`
- `0061A4C6: mov byte ptr [ebp - 4], 5`
- `0061A4EA: mov byte ptr [ebp - 4], 4`
- `0061A4FA: mov byte ptr [ebp - 4], 1`
- `0061A5AF: mov byte ptr [ebp - 4], 1`
- `0061A5DB: and byte ptr [ebp - 4], 0`
- `0061A613: and dword ptr [0xbeda94], 0`
- `0061A642: and dword ptr [0xbeda6c], 0`
- `0061A694: and dword ptr [0xbeda48], 0`
- `0061A69C: and dword ptr [0xbeda44], 0`
- `0061A6A4: and dword ptr [0xbeda40], 0`
- `0061A6AC: and dword ptr [0xbeda34], 0`
- `0061A6B7: cmp dword ptr [esi + 4], 0`
- `0061A6C4: and dword ptr [esi + 4], 0`
- `0061BAA4: or byte ptr [0xbf6ad0], 1`
- `0061BAAB: and dword ptr [0xbf6b44], 0`
- `0061CF75: and dword ptr [ebp - 4], 0`
- `0061CFB1: mov dword ptr [ebp - 4], 1`
- `0061CFE8: mov byte ptr [ebp - 4], 2`
- `0061CFF4: mov byte ptr [ebp - 4], 1`
- `0061D0D8: mov byte ptr [ebp - 4], 6`
- `0061D0EA: mov byte ptr [ebp - 4], 5`
- `0061D0F9: mov byte ptr [ebp - 4], 4`
- `0061D108: mov byte ptr [ebp - 4], 3`
- `0061D117: mov byte ptr [ebp - 4], 2`
- `0061D126: mov byte ptr [ebp - 4], 1`
- `0061D135: and byte ptr [ebp - 4], 0`
- `0061D17A: and dword ptr [ebp - 4], 0`
- `0061D1BF: cmp dword ptr [ecx + 4], 0`
- `0061D1E2: cmp dword ptr [ebp + 0xc], 4`
- `0061D212: mov byte ptr [ebp - 4], 2`
- `0061D24D: mov byte ptr [ebp - 4], 3`
- `0061D374: and dword ptr [ebp - 0x10], 0`
- `0061D38A: and dword ptr [ebp - 4], 0`
- `0061D3D1: cmp dword ptr [ecx + 4], 0`
- `0061D41C: mov byte ptr [ebp - 4], 2`
- `0061D590: mov byte ptr [ebp - 4], 2`
- `0061D5CA: mov byte ptr [ebp - 4], 3`
- `0061D6AF: and dword ptr [ebp - 4], 0`
- `0061D6F2: cmp dword ptr [esi + 4], 0`
- `0061D73E: mov byte ptr [ebp - 4], 2`
- `0061D7C2: mov dword ptr [eax], 1`
- `0061D7EC: mov byte ptr [ebp - 4], 1`
- `0061D810: mov byte ptr [ebp - 4], 3`
- `0061D832: mov byte ptr [ebp - 4], 4`
- `0061D85E: mov byte ptr [ebp - 4], 3`
- `0061D884: mov byte ptr [ebp - 4], 5`
- `0061D898: mov byte ptr [ebp - 4], 6`
- `0061D8C9: cmp dword ptr [ebp + 8], 0`
- `0061D94E: mov byte ptr [ebp - 4], 6`
- `0061D966: mov byte ptr [ebp - 4], 5`
- `0061D97E: mov byte ptr [ebp - 4], 3`
- `0061DA14: mov byte ptr [ebp - 4], 3`
- `0061DA37: mov byte ptr [ebp - 4], 3`
- `0061DA8C: and dword ptr [ebp - 4], 0`
- `0061DAF1: cmp dword ptr [ecx + 0x14], 0`
- `0061DBFA: mov byte ptr [ebp - 4], 1`
- `0061DC03: and byte ptr [ebp - 4], 0`
- `0061DC27: mov byte ptr [ebp - 4], 2`
- `0061DC40: mov byte ptr [ebp - 4], 3`
- `0061DC5C: mov byte ptr [ebp - 4], 3`
- `0061DC75: mov byte ptr [ebp - 4], 5`
- `0061DCA8: mov byte ptr [ebp - 4], 3`
- `0061DCC0: mov byte ptr [ebp - 4], 2`
- `0061DCD4: and byte ptr [ebp - 4], 0`
- `0061DD15: mov dword ptr [ebp - 0x20], 1`
- `0061DEAB: and dword ptr [ebp - 0x58], 0`
- `0061DEC8: mov dword ptr [ebp - 0x54], 1`
- `0061DF32: and byte ptr [ebp - 4], 0`
- `0061DF41: mov dword ptr [ebp - 0x20], 1`
- `0061DFD5: and byte ptr [ebp - 4], 0`
- `0061DFE9: mov dword ptr [ebp - 0x20], 1`
- `0061E102: and dword ptr [ebp - 0x58], 0`
- `0061E11F: mov dword ptr [ebp - 0x54], 1`
- `0061E189: and byte ptr [ebp - 4], 0`
- `0061E198: mov dword ptr [ebp - 0x20], 1`
- `0061E1AE: mov byte ptr [ebp - 4], 6`
- `0061E1CE: mov byte ptr [ebp - 4], 6`
- `0061E205: mov byte ptr [ebp - 4], 6`
- `0061E254: mov byte ptr [ebp - 4], 6`
- `0061E286: mov byte ptr [ebp - 4], 6`
- `0061E2A9: and byte ptr [ebp - 4], 0`
- `0061E2F8: cmp dword ptr [esi + 0xdc], 3`
- `0061E307: cmp dword ptr [esi + 0xdc], 1`
- `0061E36B: and dword ptr [ebp - 4], 0`
- `0061E3E8: mov dword ptr [ebp - 4], 1`
- `0061E434: mov dword ptr [ebp - 4], 2`
- `0061E483: and dword ptr [ebp - 4], 0`
- `0061E513: and dword ptr [ebp - 4], 0`
- `0061E527: cmp dword ptr [esi], 0`
- `0061E52A: mov byte ptr [ebp - 4], 1`
- `0061E56B: and byte ptr [ebp - 4], 0`
- `0061E5B1: cmp dword ptr [esp + 0xc], 0`
- `0061E5E7: and dword ptr [0xbeda9c], 0`
- `0061E636: cmp dword ptr [esi + 4], 0`
- `0061E643: and dword ptr [esi + 4], 0`
- `0061F4FA: or byte ptr [0xbf6ad0], 1`
- `0061F501: and dword ptr [0xbf6b44], 0`
