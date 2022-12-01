"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const core_1 = require("@nestjs/core");
const app_module_1 = require("./app.module");
const express_rate_limit_1 = require("express-rate-limit");
const cookieParser = require("cookie-parser");
async function bootstrap() {
    const app = await core_1.NestFactory.create(app_module_1.AppModule);
    const corsOptions = {
        credentials: true,
        origin: true
    };
    await app.enableCors(corsOptions);
    const limiter = (0, express_rate_limit_1.default)({
        windowMs: 15 * 60 * 1000,
        max: 500,
    });
    app.use(limiter);
    app.use(cookieParser());
    await app.listen(3001);
}
bootstrap();
//# sourceMappingURL=main.js.map