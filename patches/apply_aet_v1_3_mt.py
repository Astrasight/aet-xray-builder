from pathlib import Path
import sys

ROOT = Path.cwd()


def read_rel(rel):
    p = ROOT / rel
    if not p.is_file():
        raise RuntimeError(f"missing source file: {rel}")
    return p, p.read_text(encoding="utf-8").replace("\r\n", "\n")


def write_rel(p, text):
    p.write_text(text, encoding="utf-8", newline="\n")


def replace_once(rel, old, new, label):
    p, text = read_rel(rel)
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match in {rel}, found {count}")
    text = text.replace(old, new, 1)
    write_rel(p, text)
    print(f"[AET v1.3 MT] {label}: OK")


def insert_after(rel, anchor, addition, label):
    replace_once(rel, anchor, anchor + addition, label)


# -----------------------------------------------------------------------------
# Shader constant bindings
# -----------------------------------------------------------------------------
insert_after(
    "src/Layers/xrRender/Blender_Recorder_StandartBinding.cpp",
    '#include "dxRenderDeviceRender.h"\n',
    '#include "xrRender_console.h"\n',
    "renderer console include",
)

insert_after(
    "src/Layers/xrRender/Blender_Recorder_StandartBinding.cpp",
    'static cl_VPtexgen binder_VPtexgen;\n',
    r'''

class cl_aet_refl_cam0 : public R_constant_setup
{
    virtual void setup(R_constant* C) { RCache.set_c(C, g_aet_refl_cam0); }
};
class cl_aet_refl_cam1 : public R_constant_setup
{
    virtual void setup(R_constant* C) { RCache.set_c(C, g_aet_refl_cam1); }
};
class cl_aet_refl_cam2 : public R_constant_setup
{
    virtual void setup(R_constant* C) { RCache.set_c(C, g_aet_refl_cam2); }
};

static cl_aet_refl_cam0 binder_aet_refl_cam0;
static cl_aet_refl_cam1 binder_aet_refl_cam1;
static cl_aet_refl_cam2 binder_aet_refl_cam2;
''',
    "reflection constant binders",
)

insert_after(
    "src/Layers/xrRender/Blender_Recorder_StandartBinding.cpp",
    '\tr_Constant("m_inv_V", &binder_inv_v);\n',
    '\tr_Constant("aet_refl_cam0", &binder_aet_refl_cam0);\n'
    '\tr_Constant("aet_refl_cam1", &binder_aet_refl_cam1);\n'
    '\tr_Constant("aet_refl_cam2", &binder_aet_refl_cam2);\n',
    "reflection constants mapping",
)

# -----------------------------------------------------------------------------
# Console variables / commands
# -----------------------------------------------------------------------------
insert_after(
    "src/Layers/xrRender/xrRender_console.cpp",
    'int scope_3D_fake_enabled = 0; // Redotix99: for 3D Shader Based Scopes\n',
    r'''

int   ps_r_aet_lens_reflect = 0;
int   ps_r_aet_lens_reflect_cadence = 4;
float ps_r_aet_lens_reflect_fov = 120.0f;
int   ps_r_aet_lens_reflect_probe = 1;
int   ps_r_aet_lens_reflect_local_lights = 1;

Fvector4 g_aet_refl_cam0 = {1.f, 0.f, 0.f, 1.7320508f};
Fvector4 g_aet_refl_cam1 = {0.f, 1.f, 0.f, 0.f};
Fvector4 g_aet_refl_cam2 = {0.f, 0.f, 1.f, 0.5625f};
''',
    "reflection globals",
)

insert_after(
    "src/Layers/xrRender/xrRender_console.cpp",
    '\tCMD4(CCC_Integer, "r__3Dfakescope", &scope_3D_fake_enabled, 0, 1); // Redotix99: for 3D Shader Based Scopes\n',
    '\tCMD4(CCC_Integer, "r__aet_lens_reflect", &ps_r_aet_lens_reflect, 0, 1);\n'
    '\tCMD4(CCC_Integer, "r__aet_lens_reflect_cadence", &ps_r_aet_lens_reflect_cadence, 1, 8);\n'
    '\tCMD4(CCC_Float, "r__aet_lens_reflect_fov", &ps_r_aet_lens_reflect_fov, 90.f, 140.f);\n'
    '\tCMD4(CCC_Integer, "r__aet_lens_reflect_probe", &ps_r_aet_lens_reflect_probe, 0, 1);\n'
    '\tCMD4(CCC_Integer, "r__aet_lens_reflect_local_lights", &ps_r_aet_lens_reflect_local_lights, 0, 1);\n',
    "reflection console commands",
)

insert_after(
    "src/Layers/xrRender/xrRender_console.h",
    'extern ECORE_API int scope_3D_fake_enabled; // Redotix99: for 3D Shader Based Scopes\n',
    r'''

// Aeternelle: real 3DSS reflected-cone scene capture.
// v1.3 MT targets R4 / SDR / no-MSAA first.
extern ECORE_API int   ps_r_aet_lens_reflect;
extern ECORE_API int   ps_r_aet_lens_reflect_cadence;
extern ECORE_API float ps_r_aet_lens_reflect_fov;
extern ECORE_API int   ps_r_aet_lens_reflect_probe;
extern ECORE_API int   ps_r_aet_lens_reflect_local_lights;

extern ECORE_API Fvector4 g_aet_refl_cam0; // right.xyz, tan(vertical FOV / 2)
extern ECORE_API Fvector4 g_aet_refl_cam1; // up.xyz, live validity
extern ECORE_API Fvector4 g_aet_refl_cam2; // forward.xyz, Device.fASPECT (H/W)
''',
    "reflection console declarations",
)

# -----------------------------------------------------------------------------
# R4 renderer state
# -----------------------------------------------------------------------------
insert_after(
    "src/Layers/xrRenderPC_R4/r4.h",
    '\tbool m_bFirstFrameAfterReset; // Determines weather the frame is the first after resetting device.\n',
    r'''

    bool m_aetReflectionCapturePass;
    bool m_aetLensProbeValid;
    u32  m_aetLastCaptureFrame;
    u32  m_aetLastLensVisibleFrame;
    Fvector m_aetLensProbePosition;
    Fvector m_aetLensProbeForward;
    Fvector m_aetLensProbeUp;
    xr_vector<light*> m_aetCaptureLights;
''',
    "R4 reflection state",
)

insert_after(
    "src/Layers/xrRenderPC_R4/r4.h",
    '\tvoid render_rain();\n',
    r'''

    void AetTryCaptureReflection();
    void AetSetReflectionCamera(const Fvector& mainDir, const Fvector& mainTop);
    void AetUpdateLensProbe();
    void AetCollectCaptureLocalLights();
    void AetRenderCaptureLocalLights();
    IC bool IsAetReflectionCapture() const { return m_aetReflectionCapturePass; }
''',
    "R4 reflection methods",
)

insert_after(
    "src/Layers/xrRenderPC_R4/r4.cpp",
    'void CRender::reset_begin()\n{\n',
    r'''    g_aet_refl_cam1.w = 0.0f;
    m_aetReflectionCapturePass = false;
    m_aetLensProbeValid = false;
    m_aetLastCaptureFrame = 0;
    m_aetLastLensVisibleFrame = 0;
    m_aetCaptureLights.clear();

''',
    "reset reflection state",
)

replace_once(
    "src/Layers/xrRenderPC_R4/r4.cpp",
    'CRender::CRender()\n\t: m_bFirstFrameAfterReset(false)\n{\n\tinit_cacades();\n}',
    '''CRender::CRender()\n\t: m_bFirstFrameAfterReset(false),\n\t  m_aetReflectionCapturePass(false),\n\t  m_aetLensProbeValid(false),\n\t  m_aetLastCaptureFrame(0),\n\t  m_aetLastLensVisibleFrame(0)\n{\n\tm_aetLensProbePosition.set(0.f, 0.f, 0.f);\n\tm_aetLensProbeForward.set(0.f, 0.f, 1.f);\n\tm_aetLensProbeUp.set(0.f, 1.f, 0.f);\n\tMsg("* Aeternelle 3DSS reflected-cone v1.3 MT renderer hooks loaded");\n\tinit_cacades();\n}''',
    "R4 constructor",
)

# -----------------------------------------------------------------------------
# MT dsgraph isolation: do not let secondary camera poison CROS/HOM state.
# -----------------------------------------------------------------------------
replace_once(
    "src/Layers/xrRender/r__dsgraph_render.cpp",
    '''\t\t\tu32 uID_LTRACK = u32(-1);\n\t\t\tif (i_mask[CDSGraphManager::fl_normal])//normal phase\n\t\t\t{\n\t\t\t\t// update light-vis for current entity / actor\n''',
    '''\t\t\tu32 uID_LTRACK = u32(-1);\n\t\t\tbool aet_capture = false;\n#if RENDER==R_R4\n\t\t\taet_capture = RImplementation.IsAetReflectionCapture();\n#endif\n\t\t\tif (i_mask[CDSGraphManager::fl_normal] && !aet_capture)//normal phase\n\t\t\t{\n\t\t\t\t// update light-vis for current entity / actor\n''',
    "MT CROS isolation",
)

replace_once(
    "src/Layers/xrRender/r__dsgraph_render.cpp",
    '''\t\t\t\tif (i_mask[CDSGraphManager::fl_normal] && !RImplementation.HOM.visible(spatial->spatial.sphere))\n\t\t\t\t\tcontinue;\n''',
    '''\t\t\t\tif (i_mask[CDSGraphManager::fl_normal] && !aet_capture && !RImplementation.HOM.visible(spatial->spatial.sphere))\n\t\t\t\t\tcontinue;\n''',
    "MT dynamic HOM isolation",
)

# -----------------------------------------------------------------------------
# Dedicated reflection RT / same-frame accumulator reset
# -----------------------------------------------------------------------------
insert_after(
    "src/Layers/xrRenderPC_R4/r4_rendertarget.h",
    '\tref_rt rt_secondVP;\t// 32bit\t\t(r,g,b,a) --//#SM+#-- +SecondVP+\n',
    '\tref_rt rt_aet_lens_reflection; // Aeternelle reflected-cone scene\n',
    "reflection RT declaration",
)

insert_after(
    "src/Layers/xrRenderPC_R4/r4_rendertarget.h",
    '\tvoid increment_light_marker();\n',
    '\tvoid aet_force_accumulator_clear();\n',
    "accumulator reset declaration",
)

insert_after(
    "src/Layers/xrRenderPC_R4/r4_rendertarget.cpp",
    '\t\trt_fakescope.create(r2_RT_scopert, w, h, D3DFMT_A8R8G8B8, 1); //crookr fakescope\n',
    r'''

        // Aeternelle v1.3 MT: full-size SDR target for exact Generic_0 copy.
        rt_aet_lens_reflection.create(
            "$user$aet_lens_reflection",
            w, h,
            D3DFMT_A8R8G8B8,
            1);
''',
    "reflection RT creation",
)

replace_once(
    "src/Layers/xrRenderPC_R4/r4_rendertarget.cpp",
    'void CRenderTarget::reset_light_marker(bool bResetStencil)\n',
    '''void CRenderTarget::aet_force_accumulator_clear()\n{\n\t// Secondary and main views share Device.dwFrame; force a fresh accumulator.\n\tdwAccumulatorClearMark = u32(-1);\n}\n\nvoid CRenderTarget::reset_light_marker(bool bResetStencil)\n''',
    "accumulator reset implementation",
)

# -----------------------------------------------------------------------------
# MT R4 render path
# -----------------------------------------------------------------------------
insert_after(
    "src/Layers/xrRenderPC_R4/r4_R_render.cpp",
    '#include "../xrRender/QueryHelper.h"\n',
    '#include "../xrRender/xrRender_console.h"\n',
    "R4 reflection console include",
)

insert_after(
    "src/Layers/xrRenderPC_R4/r4_R_render.cpp",
    '''\tif (m_bFirstFrameAfterReset)\n\t{\n\t\tfor (light* L : v_all_lights)//critical!!!\n\t\t\tL->m_moving_frames = 0;\n\n\t\tm_bFirstFrameAfterReset = false;\n\t\treturn;\n\t}\n''',
    r'''

    // MT v1.3 renders the secondary objective view first. The normal frame then
    // rebuilds the graph and overwrites all scratch render targets immediately.
    if (!m_aetReflectionCapturePass)
        AetTryCaptureReflection();
''',
    "pre-main reflection capture hook",
)

replace_once(
    "src/Layers/xrRenderPC_R4/r4_R_render.cpp",
    '\tif ((Device.dwFrame % (u32)ps_r__tex_evict_interval) == 0)\n',
    '\tif (!m_aetReflectionCapturePass && (Device.dwFrame % (u32)ps_r__tex_evict_interval) == 0)\n',
    "capture texture eviction guard",
)

insert_after(
    "src/Layers/xrRenderPC_R4/r4_R_render.cpp",
    '\tif (o.sunstatic) bSUN = FALSE;\n',
    '\tif (m_aetReflectionCapturePass) bSUN = FALSE; // capture uses ambient + stable shadowless local lights\n',
    "capture sun guard",
)

replace_once(
    "src/Layers/xrRenderPC_R4/r4_R_render.cpp",
    '''\t// HOM\n\tViewBase.CreateFromMatrix(Device.mFullTransform, FRUSTUM_P_LRTB + FRUSTUM_P_FAR);\n    HOM.MT_RENDER();\n''',
    '''\t// HOM: never rebuild the shared MT HOM from the secondary objective camera.\n\tViewBase.CreateFromMatrix(Device.mFullTransform, FRUSTUM_P_LRTB + FRUSTUM_P_FAR);\n    if (!m_aetReflectionCapturePass)\n        HOM.MT_RENDER();\n''',
    "MT HOM render guard",
)

insert_after(
    "src/Layers/xrRenderPC_R4/r4_R_render.cpp",
    '''    GMBase.traverse(RImplementation.pLastSector, ViewBase, Device.vCameraPosition, Device.mFullTransform);\n    GMBase.r_dsgraph_capture_static();\n    GMBase.r_dsgraph_capture_dynamic();\n''',
    '''\n    if (m_aetReflectionCapturePass)\n        AetCollectCaptureLocalLights();\n''',
    "capture local-light collection",
)

replace_once(
    "src/Layers/xrRenderPC_R4/r4_R_render.cpp",
    '    if (RImplementation.o.ssfx_motionvectors)\n',
    '    if (RImplementation.o.ssfx_motionvectors && !m_aetReflectionCapturePass)\n',
    "motion-vector guard",
)

replace_once(
    "src/Layers/xrRenderPC_R4/r4_R_render.cpp",
    '\tif (scope_3D_fake_enabled)\n\t{\n\t\tID3D11Resource* zbuffer_res;\n',
    '\tif (scope_3D_fake_enabled && !m_aetReflectionCapturePass)\n\t{\n\t\tID3D11Resource* zbuffer_res;\n',
    "3DSS main depth guard",
)

replace_once(
    "src/Layers/xrRenderPC_R4/r4_R_render.cpp",
    '''\t{\n\t\tPIX_EVENT(DEFER_TEST_LIGHT_VIS);\n\t\t//******* Occlusion testing of volume-limited light-sources\n\t\tTarget->phase_occq();\n\t\tLP_normal.clear();\n\t\tLP_pending.clear();\n\t\tGMBase.r_dsgraph_capture_lights();\n\t}\n''',
    '''\tif (!m_aetReflectionCapturePass)\n\t{\n\t\tPIX_EVENT(DEFER_TEST_LIGHT_VIS);\n\t\t//******* Occlusion testing of volume-limited light-sources\n\t\tTarget->phase_occq();\n\t\tLP_normal.clear();\n\t\tLP_pending.clear();\n\t\tGMBase.r_dsgraph_capture_lights();\n\t}\n\telse\n\t{\n\t\tLP_normal.clear();\n\t\tLP_pending.clear();\n\t}\n''',
    "capture OCCQ/light-package guard",
)

replace_once(
    "src/Layers/xrRenderPC_R4/r4_R_render.cpp",
    '''\t\tTarget->phase_scene_begin();\n\t\tGMBase.r_dsgraph_capture_hud();\n\t\tGMBase.r_dsgraph_render_hud();\n\t\tGMBase.r_dsgraph_render_lods(true,true);\n\t\tif (Details) Details->Render();\n\t\tTarget->phase_scene_end();\n''',
    '''\t\tTarget->phase_scene_begin();\n\t\tif (!m_aetReflectionCapturePass)\n\t\t{\n\t\t\tGMBase.r_dsgraph_capture_hud();\n\t\t\tGMBase.r_dsgraph_render_hud();\n\t\t}\n\t\tGMBase.r_dsgraph_render_lods(true,true);\n\t\tif (Details && !m_aetReflectionCapturePass) Details->Render();\n\t\tTarget->phase_scene_end();\n''',
    "capture HUD/details guard",
)

replace_once(
    "src/Layers/xrRenderPC_R4/r4_R_render.cpp",
    '\tif (Wallmarks)\n',
    '\tif (Wallmarks && !m_aetReflectionCapturePass)\n',
    "capture wallmark guard",
)

replace_once(
    "src/Layers/xrRenderPC_R4/r4_R_render.cpp",
    '\tif (ps_r2_ls_flags.test(R3FLAG_DYN_WET_SURF))\n',
    '\tif (ps_r2_ls_flags.test(R3FLAG_DYN_WET_SURF) && !m_aetReflectionCapturePass)\n',
    "capture rain-wet guard",
)

replace_once(
    "src/Layers/xrRenderPC_R4/r4_R_render.cpp",
    '\t\t\tif (!Device.m_SecondViewport.IsSVPFrame())\n',
    '\t\t\tif (!Device.m_SecondViewport.IsSVPFrame() && !m_aetReflectionCapturePass)\n',
    "capture matrix-history guard",
)

replace_once(
    "src/Layers/xrRenderPC_R4/r4_R_render.cpp",
    '\t\tif (RImplementation.o.ssfx_sss && !Device.m_SecondViewport.IsSVPFrame())\n',
    '\t\tif (RImplementation.o.ssfx_sss && !Device.m_SecondViewport.IsSVPFrame() && !m_aetReflectionCapturePass)\n',
    "capture SSS guard",
)

replace_once(
    "src/Layers/xrRenderPC_R4/r4_R_render.cpp",
    '\tif (RImplementation.o.ssfx_bloom)\n\t{\n\t\t// Render Emissive on `rt_ssfx_bloom_emissive`\n',
    '\tif (RImplementation.o.ssfx_bloom && !m_aetReflectionCapturePass)\n\t{\n\t\t// Render Emissive on `rt_ssfx_bloom_emissive`\n',
    "capture bloom-emissive guard",
)

replace_once(
    "src/Layers/xrRenderPC_R4/r4_R_render.cpp",
    '''\t// Lighting, non dependant on OCCQ\n\t{\n\t\tPIX_EVENT(DEFER_LIGHT_NO_OCCQ);\n\t\tTarget->phase_accumulator();\n\t\trender_lights(LP_normal);\n\t}\n\n\t// Lighting, dependant on OCCQ\n\t{\n\t\tPIX_EVENT(DEFER_LIGHT_OCCQ);\n\t\trender_lights(LP_pending);\n\t}\n''',
    '''\t// Lighting, non dependant on OCCQ\n\t{\n\t\tPIX_EVENT(DEFER_LIGHT_NO_OCCQ);\n\t\tTarget->phase_accumulator();\n\t\tif (!m_aetReflectionCapturePass)\n\t\t\trender_lights(LP_normal);\n\t\telse\n\t\t\tAetRenderCaptureLocalLights();\n\t}\n\n\t// Lighting, dependant on OCCQ\n\tif (!m_aetReflectionCapturePass)\n\t{\n\t\tPIX_EVENT(DEFER_LIGHT_OCCQ);\n\t\trender_lights(LP_pending);\n\t}\n''',
    "capture local-light accumulation",
)

replace_once(
    "src/Layers/xrRenderPC_R4/r4_R_render.cpp",
    '\t\tif (RImplementation.o.ssfx_volumetric)\n\t\t\tTarget->phase_ssfx_volumetric_blur();\n',
    '\t\tif (RImplementation.o.ssfx_volumetric && !m_aetReflectionCapturePass)\n\t\t\tTarget->phase_ssfx_volumetric_blur();\n',
    "capture volumetric guard",
)

replace_once(
    "src/Layers/xrRenderPC_R4/r4_R_render.cpp",
    '''\tif (Details)\n\t\tDetails->details_clear();\n\n\tif (g_hud)\n''',
    '''\tif (Details && !m_aetReflectionCapturePass)\n\t\tDetails->details_clear();\n\n\tif (g_hud && !m_aetReflectionCapturePass)\n''',
    "capture end-of-render guard",
)

# Insert implementation before CHudInitializer include.
replace_once(
    "src/Layers/xrRenderPC_R4/r4_R_render.cpp",
    '}\n#include "../xrRender/CHudInitializer.h"\n',
    r'''}

namespace
{
struct SAetSavedCamera
{
    Fmatrix view, invView, project, invProject, full, invFull, fullHud;
    Fvector pos, dir, top, right;
    float fov, aspect;
};

static void AetSaveCamera(SAetSavedCamera& s)
{
    s.view = Device.mView;
    s.invView = Device.mInvView;
    s.project = Device.mProject;
    s.invProject = Device.mInvProject;
    s.full = Device.mFullTransform;
    s.invFull = Device.mInvFullTransform;
    s.fullHud = Device.mFullTransformHud;
    s.pos = Device.vCameraPosition;
    s.dir = Device.vCameraDirection;
    s.top = Device.vCameraTop;
    s.right = Device.vCameraRight;
    s.fov = Device.fFOV;
    s.aspect = Device.fASPECT;
}

static void AetRestoreCamera(const SAetSavedCamera& s)
{
    Device.mView = s.view;
    Device.mInvView = s.invView;
    Device.mProject = s.project;
    Device.mInvProject = s.invProject;
    Device.mFullTransform = s.full;
    Device.mInvFullTransform = s.invFull;
    Device.mFullTransformHud = s.fullHud;
    Device.vCameraPosition = s.pos;
    Device.vCameraDirection = s.dir;
    Device.vCameraTop = s.top;
    Device.vCameraRight = s.right;
    Device.fFOV = s.fov;
    Device.fASPECT = s.aspect;

    RCache.set_xform_view(Device.mView);
    RCache.set_xform_project(Device.mProject);
}
}

void CRender::AetSetReflectionCamera(const Fvector& mainDir, const Fvector& mainTop)
{
    Fvector forward;
    forward.set(mainDir).mul(-1.f).normalize_safe();

    Fvector right;
    right.crossproduct(mainTop, forward).normalize_safe();

    Fvector up;
    up.crossproduct(forward, right).normalize_safe();

    Device.vCameraDirection.set(forward);
    Device.vCameraTop.set(up);
    Device.vCameraRight.set(right);
    Device.fFOV = ps_r_aet_lens_reflect_fov;

    Device.mView.build_camera_dir(Device.vCameraPosition, forward, up);
    Device.mInvView.invert(Device.mView);

    Device.mProject.build_projection(
        deg2rad(Device.fFOV),
        Device.fASPECT,
        VIEWPORT_NEAR,
        g_pGamePersistent->Environment().CurrentEnv->far_plane);
    Device.mInvProject.invert(Device.mProject);

    Device.mFullTransform.mul(Device.mProject, Device.mView);
    Device.mInvFullTransform.invert(Device.mFullTransform);
    Device.mFullTransformHud.set(Device.mFullTransform);

    RCache.set_xform_view(Device.mView);
    RCache.set_xform_project(Device.mProject);

    const float tanHalfVertical = tanf(deg2rad(Device.fFOV * 0.5f));
    g_aet_refl_cam0.set(right.x, right.y, right.z, tanHalfVertical);
    g_aet_refl_cam1.set(up.x, up.y, up.z, 0.0f);
    g_aet_refl_cam2.set(forward.x, forward.y, forward.z, Device.fASPECT);
}

void CRender::AetUpdateLensProbe()
{
    m_aetLensProbeValid = false;

    float bestSSA = -1.f;
    for (const auto& item : GMBase.RGraph.mapScopeHUDSorted)
    {
        if (!item.pVisual || !item.pMatrix || item.ssa < bestSSA)
            continue;

        Fvector worldCenter;
        item.pMatrix->transform_tiny(worldCenter, item.pVisual->vis.sphere.P);
        if (!_valid(worldCenter))
            continue;

        Fvector forward = item.pMatrix->k;
        Fvector up = item.pMatrix->j;
        if (forward.square_magnitude() < EPS_S || up.square_magnitude() < EPS_S)
            continue;

        forward.normalize();
        up.normalize();

        if (forward.dotproduct(Device.vCameraDirection) < 0.f)
            forward.mul(-1.f);
        if (up.dotproduct(Device.vCameraTop) < 0.f)
            up.mul(-1.f);

        up.mad(up, forward, -up.dotproduct(forward));
        if (up.square_magnitude() < EPS_S)
            continue;
        up.normalize();

        bestSSA = item.ssa;
        m_aetLensProbePosition.set(worldCenter);
        m_aetLensProbeForward.set(forward);
        m_aetLensProbeUp.set(up);
        m_aetLensProbeValid = true;
    }
}

void CRender::AetCollectCaptureLocalLights()
{
    m_aetCaptureLights.clear();

    if (!ps_r_aet_lens_reflect_local_lights)
        return;

    // Do not export lights through CLight_DB here: that stamps frame_render and
    // would make the real MT main view reject the same lights later this frame.
    for (light* L : v_all_lights)
    {
        if (!L || !L->flags.bActive || L->flags.bStatic || L->get_hud_mode())
            continue;

        if (L->flags.type != IRender_Light::POINT && L->flags.type != IRender_Light::SPOT)
            continue;

        if (L->get_LOD() <= ps_r2_shadow_lod_min)
            continue;

        if (!L->has_light_visible_from_sectors(GMBase))
            continue;

        m_aetCaptureLights.push_back(L);
    }
}

void CRender::AetRenderCaptureLocalLights()
{
    if (!ps_r_aet_lens_reflect_local_lights || m_aetCaptureLights.empty())
        return;

    for (light* L : m_aetCaptureLights)
    {
        if (!L || !L->flags.bActive)
            continue;

        const bool savedShadow = !!L->flags.bShadow;
        const bool savedVolumetric = !!L->flags.bVolumetric;

        L->flags.bShadow = FALSE;
        L->flags.bVolumetric = FALSE;
        L->xform_calc();

        if (L->flags.type == IRender_Light::POINT)
            Target->accum_point(L);
        else if (L->flags.type == IRender_Light::SPOT)
            Target->accum_spot(L);

        L->flags.bShadow = savedShadow;
        L->flags.bVolumetric = savedVolumetric;
    }
}

void CRender::AetTryCaptureReflection()
{
    if (!ps_r_aet_lens_reflect || m_aetReflectionCapturePass)
    {
        if (!ps_r_aet_lens_reflect)
            g_aet_refl_cam1.w = 0.0f;
        return;
    }

    if (Device.m_SecondViewport.IsSVPFrame() || !scope_3D_fake_enabled)
    {
        g_aet_refl_cam1.w = 0.0f;
        return;
    }

    // Probe comes from the previous main frame. One-frame latency keeps the
    // secondary render completely ahead of the MT main-view graph.
    if (m_aetLastLensVisibleFrame + 1 < Device.dwFrame)
    {
        m_aetLensProbeValid = false;
        g_aet_refl_cam1.w = 0.0f;
        return;
    }

    if (ps_r_aet_lens_reflect_probe && !m_aetLensProbeValid)
    {
        g_aet_refl_cam1.w = 0.0f;
        return;
    }

    // Exact CopyResource path is validated only for SDR/no-MSAA in this build.
    if (o.dx10_msaa || o.dx11_hdr10)
    {
        g_aet_refl_cam1.w = 0.0f;
        return;
    }

    const u32 cadence = _max(1, ps_r_aet_lens_reflect_cadence);
    if ((Device.dwFrame % cadence) != 0 || m_aetLastCaptureFrame == Device.dwFrame)
        return; // keep the previous valid capture between cadence frames

    if (!Target || !Target->rt_aet_lens_reflection ||
        !g_pGamePersistent || !g_pGamePersistent->Environment().CurrentEnv)
    {
        g_aet_refl_cam1.w = 0.0f;
        return;
    }

    SAetSavedCamera saved;
    AetSaveCamera(saved);

    const u32 savedGraphOptions = GMBase.i_options;
    const u32 savedLTRACK = uLastLTRACK;
    const auto savedStats = stats;
    const auto savedPhase = phase;

    Fvector captureDir = saved.dir;
    Fvector captureTop = saved.top;

    if (ps_r_aet_lens_reflect_probe && m_aetLensProbeValid)
    {
        const float probeDistance = saved.pos.distance_to(m_aetLensProbePosition);
        if (probeDistance > 2.0f)
        {
            g_aet_refl_cam1.w = 0.0f;
            return;
        }

        Device.vCameraPosition.mad(m_aetLensProbePosition, m_aetLensProbeForward, 0.02f);

        if (_abs(m_aetLensProbeForward.dotproduct(saved.dir)) > 0.70f)
        {
            captureDir.set(m_aetLensProbeForward);
            captureTop.set(m_aetLensProbeUp);
        }
    }

    m_aetReflectionCapturePass = true;
    m_aetLastCaptureFrame = Device.dwFrame;
    m_aetCaptureLights.clear();

    AetSetReflectionCamera(captureDir, captureTop);

    // The objective is only centimetres from the actor eye, so retain the real
    // main-view sector and remove HOM/fade from the secondary graph options.
    GMBase.i_options = CDSGraphManager::VQ_SSA;
    GMBase.clear();
    LP_normal.clear();
    LP_pending.clear();

    Target->aet_force_accumulator_clear();
    Target->reset_light_marker(false);

    Render();

    // Capture ran before the real frame: discard every secondary graph queue.
    GMBase.clear();
    m_aetCaptureLights.clear();
    LP_normal.clear();
    LP_pending.clear();

    m_aetReflectionCapturePass = false;
    GMBase.i_options = savedGraphOptions;
    uLastLTRACK = savedLTRACK;
    stats = savedStats;
    phase = savedPhase;
    AetRestoreCamera(saved);

    // Main view must see a fresh same-frame light accumulator.
    Target->aet_force_accumulator_clear();
    Target->reset_light_marker(false);
    rmNormal();
}

#include "../xrRender/CHudInitializer.h"
''',
    "R4 reflection implementation",
)

replace_once(
    "src/Layers/xrRenderPC_R4/r4_R_render.cpp",
    '''\t\tGMBase.r_dsgraph_render_sorted(false); // strict-sorted geoms\n\t\tg_pGamePersistent->Environment().RenderLast(); // rain/thunder-bolts\n\t\tGMBase.r_dsgraph_render_sorted_hud();\n''',
    '''\t\tGMBase.r_dsgraph_render_sorted(false); // strict-sorted geoms\n\t\tif (!m_aetReflectionCapturePass)\n\t\t{\n\t\t\tg_pGamePersistent->Environment().RenderLast(); // rain/thunder-bolts\n\t\t\tGMBase.r_dsgraph_render_sorted_hud();\n\t\t}\n''',
    "capture forward-HUD guard",
)

insert_after(
    "src/Layers/xrRenderPC_R4/r4_R_render.cpp",
    '''\tVERIFY(0 == GMBase.RGraph.mapHUDSorted.Distort.size() + GMBase.RGraph.mapStaticSorted.Distort.size() + GMBase.RGraph.mapDynamicSorted.Distort.size());\n''',
    r'''

    // Scope list is cleared by r_dsgraph_render_ScopeSorted(); capture the real
    // rendered objective transform now and use it on the next frame.
    if (!m_aetReflectionCapturePass && !GMBase.RGraph.mapScopeHUDSorted.empty())
    {
        AetUpdateLensProbe();
        if (m_aetLensProbeValid)
            m_aetLastLensVisibleFrame = Device.dwFrame;
    }
''',
    "3DSS lens probe hook",
)

# -----------------------------------------------------------------------------
# Combine: avoid temporal/main-only work, publish pre-postprocess scene and exit.
# -----------------------------------------------------------------------------
replace_once(
    "src/Layers/xrRenderPC_R4/r4_rendertarget_phase_combine.cpp",
    '''\t\tstatic Fmatrix m_saved_viewproj;\n\n\t\tif (!Device.m_SecondViewport.IsSVPFrame())\n''',
    '''\t\tstatic Fmatrix m_saved_viewproj;\n\n\t\tif (!Device.m_SecondViewport.IsSVPFrame() && !RImplementation.IsAetReflectionCapture())\n''',
    "combine history guard",
)

replace_once(
    "src/Layers/xrRenderPC_R4/r4_rendertarget_phase_combine.cpp",
    '\t\tif (!Device.m_SecondViewport.IsSVPFrame())\n\t\t{\n\t\t\t// Clear RT\n',
    '\t\tif (!Device.m_SecondViewport.IsSVPFrame() && !RImplementation.IsAetReflectionCapture())\n\t\t{\n\t\t\t// Clear RT\n',
    "combine AO/IL guard",
)

replace_once(
    "src/Layers/xrRenderPC_R4/r4_rendertarget_phase_combine.cpp",
    '\tif (RImplementation.o.ssfx_ssr && !Device.m_SecondViewport.IsSVPFrame())\n',
    '\tif (RImplementation.o.ssfx_ssr && !Device.m_SecondViewport.IsSVPFrame() && !RImplementation.IsAetReflectionCapture())\n',
    "combine SSR guard",
)

replace_once(
    "src/Layers/xrRenderPC_R4/r4_rendertarget_phase_combine.cpp",
    '\tif (RImplementation.o.ssfx_water && !Device.m_SecondViewport.IsSVPFrame())\n',
    '\tif (RImplementation.o.ssfx_water && !Device.m_SecondViewport.IsSVPFrame() && !RImplementation.IsAetReflectionCapture())\n',
    "combine water-SSR guard",
)

replace_once(
    "src/Layers/xrRenderPC_R4/r4_rendertarget_phase_combine.cpp",
    '''\t{\n\t\tif (RImplementation.o.ssfx_rain)\n\t\t{\n\t\t\tphase_ssfx_rain(); // Render a small color buffer to do the refraction and more\n''',
    '''\tif (!RImplementation.IsAetReflectionCapture())\n\t{\n\t\tif (RImplementation.o.ssfx_rain)\n\t\t{\n\t\t\tphase_ssfx_rain(); // Render a small color buffer to do the refraction and more\n''',
    "combine rain guard",
)

replace_once(
    "src/Layers/xrRenderPC_R4/r4_rendertarget_phase_combine.cpp",
    '\t\tRImplementation.render_forward();\n\t\tif (g_pGamePersistent) g_pGamePersistent->OnRenderPPUI_main(); // PP-UI\n\t}\n\n\t//\tIgor: for volumetric lights\n',
    r'''        RImplementation.render_forward();
        if (g_pGamePersistent && !RImplementation.IsAetReflectionCapture())
            g_pGamePersistent->OnRenderPPUI_main(); // PP-UI
    }

    // Aeternelle v1.3 MT: publish after sky/combine/water/forward geometry,
    // before volumetrics, bloom, distortion, sunshafts, 3DSS reticle, AA,
    // exposure and temporal history.
    if (RImplementation.IsAetReflectionCapture())
    {
        HW.pContext->CopyResource(
            rt_aet_lens_reflection->pSurface,
            rt_Generic_0->pTexture->surface_get());
        g_aet_refl_cam1.w = 1.0f;
        return;
    }

    //\tIgor: for volumetric lights
''',
    "reflection scene publish",
)

print("[AET v1.3 MT] source port completed")
