from pathlib import Path

ROOT = Path.cwd()

def read_rel(rel):
    p=ROOT/rel
    if not p.is_file():
        raise RuntimeError(f"missing source file: {rel}")
    return p, p.read_text(encoding="utf-8").replace("\r\n","\n")

def replace_once(rel, old, new, label):
    p,t=read_rel(rel)
    c=t.count(old)
    if c!=1:
        raise RuntimeError(f"{label}: expected 1 match, got {c}")
    p.write_text(t.replace(old,new,1), encoding="utf-8", newline="\n")
    print("[AET SAFE BOOT]", label)

replace_once(
 "src/Layers/xrRender/xrRender_console.cpp",
 'int scope_3D_fake_enabled = 0; // Redotix99: for 3D Shader Based Scopes\\n',
 'int ps_r_aet_lens_reflect = 0;\\nint ps_r_aet_lens_reflect_cadence = 4;\\nfloat ps_r_aet_lens_reflect_fov = 120.0f;\\n',
 "safe cvars"
)

print("[AET SAFE BOOT] runtime reflection disabled")
