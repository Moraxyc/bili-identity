import React, { useState } from "react";
import axios from "axios";

function SendCode({ onBack }) {
  const [uid, setUid] = useState("");
  const [code, setCode] = useState("");
  const [step, setStep] = useState(1);
  const [msg, setMsg] = useState("");
  const [countdown, setCountdown] = useState(0);

  const sendCode = async () => {
    setMsg("");
    try {
      const res = await axios.post("/api/auth/send", { uid });
      setMsg(res.data.message);
      setStep(2);
      startCountdown();
    } catch (e) {
      setMsg(e.response?.data?.detail || "TRANSMISSION FAILURE");
    }
  };

  const verifyCode = async () => {
    setMsg("");
    try {
      const res = await axios.post("/api/auth/verify", { uid, code });
      setMsg(res.data.message);
    } catch (e) {
      setMsg(e.response?.data?.detail || "AUTHENTICATION FAILURE");
    }
  };

  const startCountdown = () => {
    let seconds = 60;
    setCountdown(seconds);
    const timer = setInterval(() => {
      seconds--;
      setCountdown(seconds);
      if (seconds === 0) clearInterval(timer);
    }, 1000);
  };

  return (
    <div
      className="fixed inset-0 flex items-center justify-center bg-base-200"
      data-theme="biling-dark"
    >
      <div className="card w-full max-w-md mx-4 shadow-2xl bg-base-100 border border-base-300">
        <div className="card-body">
          {/* 步骤指示器 */}
          <ul className="steps steps-horizontal mb-6">
            <li className={`step ${step >= 1 ? "step-primary" : ""}`}>
              UID验证
            </li>
            <li className={`step ${step >= 2 ? "step-primary" : ""}`}>
              安全验证
            </li>
          </ul>

          {/* 标题 */}
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6 text-primary"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
              />
            </svg>
            身份验证
          </h2>

          {/* 表单内容 */}
          {step === 1 ? (
            <div className="form-control">
              <label className="label">
                <span className="label-text">哔哩哔哩 UID</span>
              </label>
              <input
                type="number"
                className="input input-bordered input-primary bg-base-200"
                placeholder="例如：123456789"
                value={uid}
                onChange={(e) => setUid(e.target.value)}
              />
              <button
                className={`btn btn-primary mt-4 gap-2 ${
                  countdown > 0 ? "btn-disabled" : ""
                }`}
                onClick={sendCode}
              >
                {countdown > 0 && (
                  <span className="loading loading-spinner"></span>
                )}
                {countdown > 0 ? `等待 ${countdown}s` : "获取验证码"}
              </button>
            </div>
          ) : (
            <div className="form-control">
              <label className="label">
                <span className="label-text">验证码</span>
              </label>
              <input
                type="number"
                className="input input-bordered input-secondary bg-base-200"
                placeholder="6位数字验证码"
                value={code}
                onChange={(e) => setCode(e.target.value)}
              />
              <button
                className={`btn btn-secondary mt-4 gap-2 ${
                  !code ? "btn-disabled" : ""
                }`}
                onClick={verifyCode}
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
                立即验证
              </button>
            </div>
          )}

          {/* 状态提示 */}
          {msg && (
            <div
              className={`alert ${
                msg.includes("失败") ? "alert-error" : "alert-success"
              } mt-4`}
            >
              <div>
                {msg.includes("失败") ? (
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="stroke-current h-6 w-6"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                ) : (
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="stroke-current h-6 w-6"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                )}
                <span>{msg}</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default SendCode;
