%% ProbLog program: PGM 1
%% Created on 2020-02-24 16:12:22.129984

0.02075119::fault("AIDS_early"); 0.00103756::fault("AILD"); 0.0103756::fault("ALIP"); 0.00363146::fault("Cat_scratch_disease"); 0.0103756::fault("Dermatopathic_laden"); 0.03112679::fault("Florid_follic_hyperp"); 0.00435775::fault("GLH_hyaline_vacular"); 0.00207512::fault("GLH_plasma_cell_type"); 0.01556339::fault("Granulomatous_laden"); 0.00415024::fault("Histiocytosis_x"); 0.00726292::fault("Infectious_mono"); 0.00622536::fault("Leprosy"); 0.0103756::fault("Lymphangiographic"); 0.0129695::fault("Mantle_zone_hyperl"); 0.00830048::fault("Necrotizing_kikuchi"); 0.01328076::fault("Necrotiz_nonKikuchi"); 0.00207512::fault("Rheumatoid_arthritis"); 0.00207512::fault("Sarcoidosis"); 0.00124507::fault("SHML"); 0.01556339::fault("Sinus_hyperplasia"); 0.0025939::fault("Syphilis"); 0.00726292::fault("Toxoplasmosis"); 0.00830048::fault("Tuberculosis"); 0.0103756::fault("Viral_NOS"); 0.00207512::fault("Whipple_s_disease"); 0.0103756::fault("L_H_nodular_HD"); 0.00415024::fault("L_H_diffuse_HD"); 0.08300477::fault("Nodular_sclerosis"); 0.0051878::fault("Cellular_phase_NSHD"); 0.00415024::fault("Syncytial_NSHD"); 0.05187798::fault("Mixed_cellularity_HD"); 0.00415024::fault("Interfollicular_HD"); 0.0051878::fault("Diffuse_fibrosis_HD"); 0.0051878::fault("Reticular_type_HD"); 0.10375597::fault("Small_cleaved__fol"); 0.05706578::fault("Mixed__fol"); 0.03112679::fault("Large_cell__fol"); 0.0051878::fault("Small_noncleaved_fol"); 0.02075119::fault("Small_lymphocytic"); 0.0103756::fault("Plasmacytoid_lyctic"); 0.0103756::fault("Mantle_zone"); 0.00415024::fault("Small_cleaved__dif"); 0.0103756::fault("Mixed__fcc_dif"); 0.13488275::fault("Large_cell__dif"); 0.01556339::fault("B_immunoblastic"); 0.02075119::fault("T_immunob_mix"); 0.01556339::fault("IBL_like_T_cell_lym"); 0.00103756::fault("Japanese_ATL"); 0.0103756::fault("Lymphoblastic"); 0.06225358::fault("Small_noncleaved_dif"); 0.0016601::fault("True_histiocytic"); 0.0016601::fault("Malig_histiocytosis"); 0.00207512::fault("Multiple_myeloma"); 0.00622536::fault("Mycosis_fungoides"); 0.0025939::fault("AML"); 0.00020751::fault("Hairy_cell_leukemia"); 0.02075119::fault("Carcinoma"); 0.00830048::fault("Melanoma"); 0.00332019::fault("Em_plasmacytoma"); 0.00830048::fault("Kaposis_sarcoma"); 0.00311268::fault("Mast_cell_disease"); 0.02075119::fault("AIDS_involutionary"); 0.02075119::fault("T_immunob_lrg").
0.0::f97("Absent"); 1.0::f97("Present") :- fault("AIDS_early").
0.99::f97("Absent"); 0.01::f97("Present") :- fault("AILD").
0.9::f97("Absent"); 0.1::f97("Present") :- fault("ALIP").
0.01::f97("Absent"); 0.99::f97("Present") :- fault("Cat_scratch_disease").
0.01::f97("Absent"); 0.99::f97("Present") :- fault("Dermatopathic_laden").
0.0::f97("Absent"); 1.0::f97("Present") :- fault("Florid_follic_hyperp").
0.0::f97("Absent"); 1.0::f97("Present") :- fault("GLH_hyaline_vacular").
0.0::f97("Absent"); 1.0::f97("Present") :- fault("GLH_plasma_cell_type").
0.01::f97("Absent"); 0.99::f97("Present") :- fault("Granulomatous_laden").
0.01::f97("Absent"); 0.99::f97("Present") :- fault("Histiocytosis_x").
0.01::f97("Absent"); 0.99::f97("Present") :- fault("Infectious_mono").
0.9::f97("Absent"); 0.1::f97("Present") :- fault("Leprosy").
0.01::f97("Absent"); 0.99::f97("Present") :- fault("Lymphangiographic").
0.0::f97("Absent"); 1.0::f97("Present") :- fault("Mantle_zone_hyperl").
0.01::f97("Absent"); 0.99::f97("Present") :- fault("Necrotizing_kikuchi").
0.01::f97("Absent"); 0.99::f97("Present") :- fault("Necrotiz_nonKikuchi").
0.0::f97("Absent"); 1.0::f97("Present") :- fault("Rheumatoid_arthritis").
0.9::f97("Absent"); 0.1::f97("Present") :- fault("Sarcoidosis").
0.01::f97("Absent"); 0.99::f97("Present") :- fault("SHML").
0.01::f97("Absent"); 0.99::f97("Present") :- fault("Sinus_hyperplasia").
0.0::f97("Absent"); 1.0::f97("Present") :- fault("Syphilis").
0.0::f97("Absent"); 1.0::f97("Present") :- fault("Toxoplasmosis").
0.9::f97("Absent"); 0.1::f97("Present") :- fault("Tuberculosis").
0.01::f97("Absent"); 0.99::f97("Present") :- fault("Viral_NOS").
0.01::f97("Absent"); 0.99::f97("Present") :- fault("Whipple_s_disease").
0.99::f97("Absent"); 0.01::f97("Present") :- fault("L_H_nodular_HD").
0.99::f97("Absent"); 0.01::f97("Present") :- fault("L_H_diffuse_HD").
0.8::f97("Absent"); 0.2::f97("Present") :- fault("Nodular_sclerosis").
0.8::f97("Absent"); 0.2::f97("Present") :- fault("Cellular_phase_NSHD").
0.8::f97("Absent"); 0.2::f97("Present") :- fault("Syncytial_NSHD").
0.8::f97("Absent"); 0.2::f97("Present") :- fault("Mixed_cellularity_HD").
0.0::f97("Absent"); 1.0::f97("Present") :- fault("Interfollicular_HD").
0.999::f97("Absent"); 0.001::f97("Present") :- fault("Diffuse_fibrosis_HD").
0.999::f97("Absent"); 0.001::f97("Present") :- fault("Reticular_type_HD").
0.0::f97("Absent"); 1.0::f97("Present") :- fault("Small_cleaved__fol").
0.0::f97("Absent"); 1.0::f97("Present") :- fault("Mixed__fol").
0.0::f97("Absent"); 1.0::f97("Present") :- fault("Large_cell__fol").
0.0::f97("Absent"); 1.0::f97("Present") :- fault("Small_noncleaved_fol").
0.95::f97("Absent"); 0.05::f97("Present") :- fault("Small_lymphocytic").
0.999::f97("Absent"); 0.001::f97("Present") :- fault("Plasmacytoid_lyctic").
0.01::f97("Absent"); 0.99::f97("Present") :- fault("Mantle_zone").
0.999::f97("Absent"); 0.001::f97("Present") :- fault("Small_cleaved__dif").
0.999::f97("Absent"); 0.001::f97("Present") :- fault("Mixed__fcc_dif").
0.999::f97("Absent"); 0.001::f97("Present") :- fault("Large_cell__dif").
0.999::f97("Absent"); 0.001::f97("Present") :- fault("B_immunoblastic").
0.8::f97("Absent"); 0.2::f97("Present") :- fault("T_immunob_mix").
0.999::f97("Absent"); 0.001::f97("Present") :- fault("IBL_like_T_cell_lym").
0.999::f97("Absent"); 0.001::f97("Present") :- fault("Japanese_ATL").
0.95::f97("Absent"); 0.05::f97("Present") :- fault("Lymphoblastic").
0.999::f97("Absent"); 0.001::f97("Present") :- fault("Small_noncleaved_dif").
0.999::f97("Absent"); 0.001::f97("Present") :- fault("True_histiocytic").
0.999::f97("Absent"); 0.001::f97("Present") :- fault("Malig_histiocytosis").
0.2::f97("Absent"); 0.8::f97("Present") :- fault("Multiple_myeloma").
0.2::f97("Absent"); 0.8::f97("Present") :- fault("Mycosis_fungoides").
0.2::f97("Absent"); 0.8::f97("Present") :- fault("AML").
0.2::f97("Absent"); 0.8::f97("Present") :- fault("Hairy_cell_leukemia").
0.2::f97("Absent"); 0.8::f97("Present") :- fault("Carcinoma").
0.2::f97("Absent"); 0.8::f97("Present") :- fault("Melanoma").
0.99::f97("Absent"); 0.01::f97("Present") :- fault("Em_plasmacytoma").
0.99::f97("Absent"); 0.01::f97("Present") :- fault("Kaposis_sarcoma").
0.99::f97("Absent"); 0.01::f97("Present") :- fault("Mast_cell_disease").
0.05::f97("Absent"); 0.95::f97("Present") :- fault("AIDS_involutionary").
0.999::f97("Absent"); 0.001::f97("Present") :- fault("T_immunob_lrg").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("AIDS_early").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("AILD").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("ALIP").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Cat_scratch_disease").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Dermatopathic_laden").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Florid_follic_hyperp").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("GLH_hyaline_vacular").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("GLH_plasma_cell_type").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Granulomatous_laden").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Histiocytosis_x").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Infectious_mono").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Leprosy").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Lymphangiographic").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Mantle_zone_hyperl").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Necrotizing_kikuchi").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Necrotiz_nonKikuchi").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Rheumatoid_arthritis").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Sarcoidosis").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("SHML").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Sinus_hyperplasia").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Syphilis").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Toxoplasmosis").
0.1::f1("Absent"); 0.9::f1("Present") :- fault("Tuberculosis").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Viral_NOS").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Whipple_s_disease").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("L_H_nodular_HD").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("L_H_diffuse_HD").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Nodular_sclerosis").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Cellular_phase_NSHD").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Syncytial_NSHD").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Mixed_cellularity_HD").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Interfollicular_HD").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Diffuse_fibrosis_HD").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Reticular_type_HD").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Small_cleaved__fol").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Mixed__fol").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Large_cell__fol").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Small_noncleaved_fol").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Small_lymphocytic").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Plasmacytoid_lyctic").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Mantle_zone").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Small_cleaved__dif").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Mixed__fcc_dif").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Large_cell__dif").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("B_immunoblastic").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("T_immunob_mix").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("IBL_like_T_cell_lym").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Japanese_ATL").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Lymphoblastic").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Small_noncleaved_dif").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("True_histiocytic").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Malig_histiocytosis").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Multiple_myeloma").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Mycosis_fungoides").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("AML").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Hairy_cell_leukemia").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Carcinoma").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Melanoma").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Em_plasmacytoma").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Kaposis_sarcoma").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("Mast_cell_disease").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("AIDS_involutionary").
1.0::f1("Absent"); 0.0::f1("Present") :- fault("T_immunob_lrg").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("AIDS_early"), f97("Absent").
0.0::f78("NA"); 0.65::f78("No"); 0.35::f78("Yes") :- fault("AIDS_early"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("AILD"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("AILD"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("ALIP"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("ALIP"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Cat_scratch_disease"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Cat_scratch_disease"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Dermatopathic_laden"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Dermatopathic_laden"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Florid_follic_hyperp"), f97("Absent").
0.0::f78("NA"); 0.98::f78("No"); 0.02::f78("Yes") :- fault("Florid_follic_hyperp"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("GLH_hyaline_vacular"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("GLH_hyaline_vacular"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("GLH_plasma_cell_type"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("GLH_plasma_cell_type"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Granulomatous_laden"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Granulomatous_laden"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Histiocytosis_x"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Histiocytosis_x"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Infectious_mono"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Infectious_mono"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Leprosy"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Leprosy"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Lymphangiographic"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Lymphangiographic"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Mantle_zone_hyperl"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Mantle_zone_hyperl"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Necrotizing_kikuchi"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Necrotizing_kikuchi"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Necrotiz_nonKikuchi"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Necrotiz_nonKikuchi"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Rheumatoid_arthritis"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Rheumatoid_arthritis"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Sarcoidosis"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Sarcoidosis"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("SHML"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("SHML"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Sinus_hyperplasia"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Sinus_hyperplasia"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Syphilis"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Syphilis"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Toxoplasmosis"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Toxoplasmosis"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Tuberculosis"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Tuberculosis"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Viral_NOS"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Viral_NOS"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Whipple_s_disease"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Whipple_s_disease"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("L_H_nodular_HD"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("L_H_nodular_HD"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("L_H_diffuse_HD"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("L_H_diffuse_HD"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Nodular_sclerosis"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Nodular_sclerosis"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Cellular_phase_NSHD"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Cellular_phase_NSHD"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Syncytial_NSHD"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Syncytial_NSHD"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Mixed_cellularity_HD"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Mixed_cellularity_HD"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Interfollicular_HD"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Interfollicular_HD"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Diffuse_fibrosis_HD"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Diffuse_fibrosis_HD"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Reticular_type_HD"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Reticular_type_HD"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Small_cleaved__fol"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Small_cleaved__fol"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Mixed__fol"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Mixed__fol"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Large_cell__fol"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Large_cell__fol"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Small_noncleaved_fol"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Small_noncleaved_fol"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Small_lymphocytic"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Small_lymphocytic"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Plasmacytoid_lyctic"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Plasmacytoid_lyctic"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Mantle_zone"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Mantle_zone"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Small_cleaved__dif"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Small_cleaved__dif"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Mixed__fcc_dif"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Mixed__fcc_dif"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Large_cell__dif"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Large_cell__dif"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("B_immunoblastic"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("B_immunoblastic"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("T_immunob_mix"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("T_immunob_mix"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("IBL_like_T_cell_lym"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("IBL_like_T_cell_lym"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Japanese_ATL"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Japanese_ATL"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Lymphoblastic"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Lymphoblastic"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Small_noncleaved_dif"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Small_noncleaved_dif"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("True_histiocytic"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("True_histiocytic"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Malig_histiocytosis"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Malig_histiocytosis"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Multiple_myeloma"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Multiple_myeloma"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Mycosis_fungoides"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Mycosis_fungoides"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("AML"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("AML"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Hairy_cell_leukemia"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Hairy_cell_leukemia"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Carcinoma"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Carcinoma"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Melanoma"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Melanoma"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Em_plasmacytoma"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Em_plasmacytoma"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Kaposis_sarcoma"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Kaposis_sarcoma"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("Mast_cell_disease"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("Mast_cell_disease"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("AIDS_involutionary"), f97("Absent").
0.0::f78("NA"); 0.9::f78("No"); 0.1::f78("Yes") :- fault("AIDS_involutionary"), f97("Present").
1.0::f78("NA"); 0.0::f78("No"); 0.0::f78("Yes") :- fault("T_immunob_lrg"), f97("Absent").
0.0::f78("NA"); 0.999::f78("No"); 0.001::f78("Yes") :- fault("T_immunob_lrg"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("AIDS_early"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("AIDS_early"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("AILD"), f97("Absent").
0.0::f2("NA"); 0.3::f2("No"); 0.7::f2("Yes") :- fault("AILD"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("ALIP"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("ALIP"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Cat_scratch_disease"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Cat_scratch_disease"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Dermatopathic_laden"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Dermatopathic_laden"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Florid_follic_hyperp"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Florid_follic_hyperp"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("GLH_hyaline_vacular"), f97("Absent").
0.0::f2("NA"); 0.0::f2("No"); 1.0::f2("Yes") :- fault("GLH_hyaline_vacular"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("GLH_plasma_cell_type"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("GLH_plasma_cell_type"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Granulomatous_laden"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Granulomatous_laden"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Histiocytosis_x"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Histiocytosis_x"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Infectious_mono"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Infectious_mono"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Leprosy"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Leprosy"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Lymphangiographic"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Lymphangiographic"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Mantle_zone_hyperl"), f97("Absent").
0.0::f2("NA"); 0.05::f2("No"); 0.95::f2("Yes") :- fault("Mantle_zone_hyperl"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Necrotizing_kikuchi"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Necrotizing_kikuchi"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Necrotiz_nonKikuchi"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Necrotiz_nonKikuchi"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Rheumatoid_arthritis"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Rheumatoid_arthritis"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Sarcoidosis"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Sarcoidosis"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("SHML"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("SHML"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Sinus_hyperplasia"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Sinus_hyperplasia"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Syphilis"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Syphilis"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Toxoplasmosis"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Toxoplasmosis"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Tuberculosis"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Tuberculosis"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Viral_NOS"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Viral_NOS"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Whipple_s_disease"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Whipple_s_disease"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("L_H_nodular_HD"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("L_H_nodular_HD"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("L_H_diffuse_HD"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("L_H_diffuse_HD"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Nodular_sclerosis"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Nodular_sclerosis"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Cellular_phase_NSHD"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Cellular_phase_NSHD"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Syncytial_NSHD"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Syncytial_NSHD"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Mixed_cellularity_HD"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Mixed_cellularity_HD"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Interfollicular_HD"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Interfollicular_HD"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Diffuse_fibrosis_HD"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Diffuse_fibrosis_HD"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Reticular_type_HD"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Reticular_type_HD"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Small_cleaved__fol"), f97("Absent").
0.0::f2("NA"); 0.99999::f2("No"); 1e-05::f2("Yes") :- fault("Small_cleaved__fol"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Mixed__fol"), f97("Absent").
0.0::f2("NA"); 0.99999::f2("No"); 1e-05::f2("Yes") :- fault("Mixed__fol"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Large_cell__fol"), f97("Absent").
0.0::f2("NA"); 0.99999::f2("No"); 1e-05::f2("Yes") :- fault("Large_cell__fol"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Small_noncleaved_fol"), f97("Absent").
0.0::f2("NA"); 0.99999::f2("No"); 1e-05::f2("Yes") :- fault("Small_noncleaved_fol"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Small_lymphocytic"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Small_lymphocytic"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Plasmacytoid_lyctic"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Plasmacytoid_lyctic"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Mantle_zone"), f97("Absent").
0.0::f2("NA"); 0.01::f2("No"); 0.99::f2("Yes") :- fault("Mantle_zone"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Small_cleaved__dif"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Small_cleaved__dif"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Mixed__fcc_dif"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Mixed__fcc_dif"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Large_cell__dif"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Large_cell__dif"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("B_immunoblastic"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("B_immunoblastic"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("T_immunob_mix"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("T_immunob_mix"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("IBL_like_T_cell_lym"), f97("Absent").
0.0::f2("NA"); 0.3::f2("No"); 0.7::f2("Yes") :- fault("IBL_like_T_cell_lym"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Japanese_ATL"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Japanese_ATL"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Lymphoblastic"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Lymphoblastic"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Small_noncleaved_dif"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Small_noncleaved_dif"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("True_histiocytic"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("True_histiocytic"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Malig_histiocytosis"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Malig_histiocytosis"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Multiple_myeloma"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Multiple_myeloma"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Mycosis_fungoides"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Mycosis_fungoides"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("AML"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("AML"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Hairy_cell_leukemia"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Hairy_cell_leukemia"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Carcinoma"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Carcinoma"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Melanoma"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Melanoma"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Em_plasmacytoma"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Em_plasmacytoma"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Kaposis_sarcoma"), f97("Absent").
0.0::f2("NA"); 0.01::f2("No"); 0.99::f2("Yes") :- fault("Kaposis_sarcoma"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("Mast_cell_disease"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("Mast_cell_disease"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("AIDS_involutionary"), f97("Absent").
0.0::f2("NA"); 0.01::f2("No"); 0.99::f2("Yes") :- fault("AIDS_involutionary"), f97("Present").
1.0::f2("NA"); 0.0::f2("No"); 0.0::f2("Yes") :- fault("T_immunob_lrg"), f97("Absent").
0.0::f2("NA"); 0.99::f2("No"); 0.01::f2("Yes") :- fault("T_immunob_lrg"), f97("Present").

query(f2(_)).
query(f78(_)).
query(f1(_)).
