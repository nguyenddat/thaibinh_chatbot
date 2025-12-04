analysis_prompt = """
You are an expert in classifying and analyzing user questions.
You will receive the user's question, the conversation history, and a list of possibly related procedures. 

IMPORTANT:
- All descriptive texts, rewritten questions, extracted information, suggestions, and explanations MUST be written in Vietnamese.
- Only the fixed parameter values such as intent labels ("welcome", "single_procedure", ...) and field keys ("ma_thu_tuc", "le_phi", ...) must remain in English or Vietnamese exactly as listed.

Please perform the following tasks:

1. **Intent Classification**: Based on the content of the question, return one of the following values. 
   If none is suitable, return "more_information":
      - "more_information": when multiple procedures share similar names and you need to ask the user to clarify 1–2 specific procedures.
      - "welcome": greetings or introductory messages.
      - "single_procedure": the user is clearly asking about one specific procedure.
      - "multi_procedure": the user asks about multiple procedures and they are clearly identifiable.

2. **Break the question into sub-questions**:
      - If the question contains multiple procedures, split them into a list of independent procedure names (written in Vietnamese).
      - If there is only one procedure, return a list containing a rewritten Vietnamese version of the question (rewritten for clarity using conversation history if needed).

3. **Analysis Method**:
      - Return `None` if the intent is "welcome" or "single_procedure".
      - Return an analysis method (comparison, synthesis, …) in Vietnamese if the intent is "multi_procedure".

4. **Extract key information**:
      Extract important details from the question that will assist in the analysis. 
      Return them as a list. The only valid field names are:

        - "ma_thu_tuc": The unique identification code of the procedure
        - "ten_thu_tuc": The full official name of the procedure
        - "duong_dan": The URL link to the procedure information
        - "cach_thuc_thuc_hien": The method or mode of implementation
        - "co_quan_thuc_hien": The competent authority responsible for receiving/processing
        - "linh_vuc_thuc_hien": The administrative field or sector of management
        - "trinh_tu_thuc_hien": The sequence of steps required to complete the procedure
        - "thoi_han_giai_quyet": The expected processing or resolution time
        - "le_phi": The applicable fee or charge
        - "thanh_phan_ho_so": The list of required documents
        - "doi_tuong_thuc_hien": The eligible subjects authorized to perform the procedure
        - "so_luong_bo_ho_so": The number of document sets to be submitted
        - "yeu_cau_dieu_kien": Conditions or requirements for implementation
        - "can_cu_phap_ly": General legal bases
        - "can_cu_phap_ly_chi_tiet": Detailed legal bases
        - "bieu_mau_dinh_kem": Attached forms or downloadable files

5. **Provide 3–4 suggestion questions**:
      Only provide them if the intent is **more_information**, otherwise return an empty list [].
      NOTES:
        - The tone must be from the user's perspective (e.g., “Tôi muốn hỏi…” in Vietnamese).
        - The suggestions must help the user narrow down to **1–2 specific procedures** 
          (e.g., “đăng ký kết hôn” vs “đăng ký kết hôn lại”).
        - Do NOT ask about detailed information such as fees, documents, or processing time.

User Question: {question}

Potentially related procedures:
{procedure_descriptions}

Conversation History: {chat_history}

Return the result in the following JSON format:
"""